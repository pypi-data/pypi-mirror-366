from rdkit import Chem
from rdkit.Chem import AllChem, rdMolTransforms
import itertools
import multiprocessing
import os
import subprocess
import shutil

def _log(message, level=1, print_level=1):
    """Simple logging function."""
    if print_level >= level:
        print(f"[Level {level}] {message}")


def process_smiles(smiles, print_level=1, no_chirality_enforced_allowed=True):
    """
    Convert SMILES to 3D, check stereochemistry, prepare for switching.
    
    Parameters:
        smiles (str): Input SMILES string
        print_level (int): Logging verbosity (0=none, 1=basic, 2=detailed)
        no_chirality_enforced_allowed (bool): Allow conformer generation without chirality enforcement
        
    Returns:
        dict: Complete processing results including molecule, stereochemistry info, and status
    """
    results = {
        'original_smiles': smiles,
        'molecule': None,
        'stereochemistry_info': {},
        'status': {'conformer_generation': None, 'stereochemistry_check': None},
        'bonds_to_switch': [],
        'ready_for_orca': False
    }
    
    _log(f"Processing SMILES: {smiles}", level=1, print_level=print_level)
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        results['status']['conformer_generation'] = 'FAILED_PARSE'
        _log(f"Error: Failed to parse SMILES: {smiles}", level=1, print_level=print_level)
        return results
    
    mol = Chem.AddHs(mol)
    _log("Added hydrogens to molecule", level=2, print_level=print_level)
    
    _log("Generating 3D conformer...", level=1, print_level=print_level)
    mol, conf_status = _create_3D_conformer(mol, print_level, no_chirality_enforced_allowed)
    if mol is None:
        results['status']['conformer_generation'] = 'FAILED'
        _log("Error: Failed to generate 3D conformer", level=1, print_level=print_level)
        return results
    
    results['molecule'] = mol
    results['status']['conformer_generation'] = conf_status
    
    _log("Checking stereochemistry...", level=1, print_level=print_level)
    stereochem_info = _check_stereochemistry(mol, smiles, print_level)
    results['stereochemistry_info'] = stereochem_info
    results['status']['stereochemistry_check'] = 'COMPLETED'
    
    bonds_to_switch = _identify_bonds_to_switch(stereochem_info)
    results['bonds_to_switch'] = bonds_to_switch
    results['ready_for_orca'] = len(bonds_to_switch) > 0
    
    _log(f"Processing completed. Found {len(bonds_to_switch)} bonds needing correction", level=1, print_level=print_level)
    return results


def _create_3D_conformer(mol, print_level, no_chirality_enforced_allowed):
    """Generate 3D conformer with multiple fallback strategies."""
    
    def is_strained_ring(mol):
        """Check for strained ring system: size < 12 with double or triple bonds."""
        ring_info = mol.GetRingInfo()
        for ring in ring_info.BondRings():
            if len(ring) < 12:
                for bond_idx in ring:
                    bond = mol.GetBondWithIdx(bond_idx)
                    if bond.GetBondType() in [Chem.BondType.DOUBLE, Chem.BondType.TRIPLE]:
                        return True
        return False
    
    def reverse_ring_stereochemistry(mol):
        """Generate molecules with reversed stereochemistry for strained rings."""
        ring_info = mol.GetRingInfo()
        double_bonds = []
        
        for ring in ring_info.BondRings():
            if len(ring) < 12:
                for bond_idx in ring:
                    bond = mol.GetBondWithIdx(bond_idx)
                    if bond.GetBondType() == Chem.BondType.DOUBLE:
                        double_bonds.append(bond_idx)
        
        reversed_mols = []
        for combination in itertools.product([True, False], repeat=len(double_bonds)):
            new_mol = Chem.Mol(mol)
            for bond_idx, reverse in zip(double_bonds, combination):
                if reverse:
                    bond = new_mol.GetBondWithIdx(bond_idx)
                    current_stereo = bond.GetStereo()
                    new_stereo = (Chem.BondStereo.STEREOZ if current_stereo == Chem.BondStereo.STEREOE 
                                else Chem.BondStereo.STEREOE)
                    bond.SetStereo(new_stereo)
            reversed_mols.append(new_mol)
        
        return reversed_mols
    
    _log("Trying ETKDGv3...", level=2, print_level=print_level)
    params = AllChem.ETKDGv3()
    if AllChem.EmbedMolecule(mol, params) == 0:
        _log("ETKDGv3 succeeded", level=2, print_level=print_level)
        return mol, 'SUCCESS_ETKDG3'
    
    _log("ETKDGv3 failed. Trying ETKDGv2...", level=2, print_level=print_level)
    params = AllChem.ETKDGv2()
    if AllChem.EmbedMolecule(mol, params) == 0:
        _log("ETKDGv2 succeeded", level=2, print_level=print_level)
        return mol, 'SUCCESS_ETKDG2'
    
    if is_strained_ring(mol):
        _log("Detected strained ring system. Trying advanced strategies...", level=1, print_level=print_level)
        
        params = AllChem.ETKDGv3()
        params.useRandomCoords = True
        conf_ids = AllChem.EmbedMultipleConfs(mol, numConfs=1, params=params)
        if len(conf_ids) > 0:
            _log("ETKDGv3 with random coordinates succeeded", level=1, print_level=print_level)
            return mol, 'SUCCESS_STRAINED'
        
        params = AllChem.ETKDGv3()
        params.useBasicKnowledge = False
        params.ignoreSmoothingFailures = True
        if AllChem.EmbedMolecule(mol, params) == 0:
            _log("ETKDGv3 with relaxed constraints succeeded", level=1, print_level=print_level)
            return mol, 'SUCCESS_RELAXED'
        
        reversed_mols = reverse_ring_stereochemistry(mol)
        for i, reversed_mol in enumerate(reversed_mols):
            params = AllChem.ETKDGv3()
            if AllChem.EmbedMolecule(reversed_mol, params) == 0:
                _log(f"ETKDGv3 with reversed stereochemistry (variant {i}) succeeded", level=1, print_level=print_level)
                return reversed_mol, 'SUCCESS_REVERSED'
        
        if no_chirality_enforced_allowed:
            params = AllChem.ETKDGv2()
            params.useRandomCoords = True
            params.useBasicKnowledge = False
            params.ignoreSmoothingFailures = True
            params.enforceChirality = False
            for attempt in range(10):
                params.randomSeed = attempt * 42
                if AllChem.EmbedMolecule(mol, params) == 0:
                    _log("ETKDGv2 without chirality enforcement succeeded", level=1, print_level=print_level)
                    return mol, 'SUCCESS_NO_CHIRALITY'
    
    _log("All conformer generation strategies failed", level=1, print_level=print_level)
    return None, 'FAILED'


def _check_stereochemistry(mol, original_smiles, print_level):
    """Check stereochemistry of all double bonds against original SMILES."""
    Chem.AssignStereochemistry(mol, cleanIt=True, force=True)
    
    original_mol = Chem.MolFromSmiles(original_smiles)
    if not original_mol:
        _log(f"Error: Failed to parse original SMILES: {original_smiles}", level=1, print_level=print_level)
        return {}
    
    stereochem_info = {}
    
    for bond in mol.GetBonds():
        if bond.GetBondType() == Chem.BondType.DOUBLE:
            bond_index = bond.GetIdx()
            
            original_bond = original_mol.GetBondBetweenAtoms(
                bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
            )
            
            if not original_bond:
                _log(f"Warning: No matching bond found for bond {bond_index}", level=2, print_level=print_level)
                continue
            
            original_stereo = _get_original_stereochemistry(original_smiles, bond_index, mol, print_level)
            structure_stereo = _get_3D_stereochemistry(mol, original_mol, bond_index, print_level)
            
            stereochem_info[bond_index] = {
                'original': original_stereo,
                'structure': structure_stereo,
                'match': original_stereo == structure_stereo,
                'bond_atoms': (bond.GetBeginAtomIdx(), bond.GetEndAtomIdx())
            }
            
            _log(f"Bond {bond_index}: Original={original_stereo}, 3D={structure_stereo}", level=2, print_level=print_level)
    
    return stereochem_info


def _get_original_stereochemistry(smiles, bond_index, mol, print_level):
    """Get stereochemistry from original SMILES, handling small rings specially."""
    original_mol = Chem.MolFromSmiles(smiles)
    bond = mol.GetBondWithIdx(bond_index)
    original_bond = original_mol.GetBondBetweenAtoms(
        bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
    )
    
    if not original_bond:
        return 'unknown'
    
    original_stereo = original_bond.GetStereo()

    if original_stereo == Chem.BondStereo.STEREONONE:
        ring_info = mol.GetRingInfo()
        in_small_ring = any(bond_index in ring and len(ring) <= 7 
                          for ring in ring_info.BondRings())
        
        if in_small_ring:
            _log(f"Bond {bond_index} in small ring - using safety-disabled analysis", level=2, print_level=print_level)
            return _analyze_small_ring_stereochemistry(smiles, bond_index, mol, print_level)
        else:
            return 'undefined'
    
    return 'cis' if original_stereo == Chem.BondStereo.STEREOZ else (
           'trans' if original_stereo == Chem.BondStereo.STEREOE else 'undefined')


def _analyze_small_ring_stereochemistry(smiles, bond_idx, mol, print_level):
    """Analyze stereochemistry in small rings using multiprocessing."""
    try:
        mol_block = Chem.MolToMolBlock(mol)
        with multiprocessing.Pool(processes=1) as pool:
            result = pool.apply(_rdkit_safety_disabled_analysis, 
                              (smiles, bond_idx, mol_block))
        return result[0] if result else 'unknown'
    except Exception as e:
        _log(f"Error in small ring analysis: {e}", level=1, print_level=print_level)
        return 'unknown'


def _rdkit_safety_disabled_analysis(smiles, bond_idx, mol_block):
    """Run RDKit analysis with safety disabled in subprocess."""
    try:
        Chem.SetUseLegacyStereoPerception(False)
        
        original_mol = Chem.MolFromSmiles(smiles, sanitize=False)
        Chem.SanitizeMol(original_mol)
        Chem.AssignStereochemistry(original_mol, cleanIt=False, force=True)
        
        bond = original_mol.GetBondWithIdx(bond_idx)
        stereo = bond.GetStereo()
        stereo_str = ('cis' if str(stereo) == "STEREOCIS" else 
                     'trans' if str(stereo) == "STEREOTRANS" else 'undefined')
        
        # Also get 3D stereochemistry for comparison
        mol = Chem.MolFromMolBlock(mol_block)
        structure_stereo = 'unknown'  # Placeholder for 3D analysis
        
        return stereo_str, structure_stereo
    except Exception:
        return 'unknown', 'unknown'


def _get_3D_stereochemistry(mol, original_mol, bond_index, print_level):
    """Determine stereochemistry from 3D coordinates using dihedral angles."""
    try:
        bond = original_mol.GetBondWithIdx(bond_index)
        begin_atom = bond.GetBeginAtom()
        end_atom = bond.GetEndAtom()

        neighbors_begin = sorted(
            [n for n in begin_atom.GetNeighbors() if n.GetIdx() != end_atom.GetIdx()],
            key=lambda x: int(x.GetProp("_CIPRank")) if x.HasProp("_CIPRank") else 0,
            reverse=False
        )
        neighbors_end = sorted(
            [n for n in end_atom.GetNeighbors() if n.GetIdx() != begin_atom.GetIdx()],
            key=lambda x: int(x.GetProp("_CIPRank")) if x.HasProp("_CIPRank") else 0,
            reverse=False
        )

        if len(neighbors_begin) < 1 or len(neighbors_end) < 1:
            _log(f"Warning: Bond {bond_index} missing neighbors", level=2, print_level=print_level)
            return 'unknown'

        atom1 = neighbors_begin[0].GetIdx()
        atom2 = begin_atom.GetIdx()
        atom3 = end_atom.GetIdx()
        atom4 = neighbors_end[0].GetIdx()

        conf = mol.GetConformer()
        dihedral = rdMolTransforms.GetDihedralDeg(conf, atom1, atom2, atom3, atom4)

        return _dihedral_to_stereo(dihedral, print_level)
        
    except Exception as e:
        _log(f"Error calculating 3D stereochemistry for bond {bond_index}: {e}", level=2, print_level=print_level)
        return 'unknown'


def _dihedral_to_stereo(dihedral, print_level):
    """Convert dihedral angle to stereochemistry label."""
    if dihedral is None:
        return 'unknown'
    
    if -30 <= dihedral <= 30:
        return 'cis'
    elif 150 <= dihedral <= 210 or -210 <= dihedral <= -150:
        return 'trans'
    else:
        _log(f"Unusual dihedral angle: {dihedral:.1f}°", level=2, print_level=print_level)
        return 'unknown'


def _identify_bonds_to_switch(stereochem_info):
    """Identify bonds that NEED to be switched to match original stereochemistry."""
    bonds_to_switch = []
    
    for bond_idx, info in stereochem_info.items():
        if (info['original'] in ['cis', 'trans'] and 
            info['structure'] in ['cis', 'trans'] and 
            not info['match']):  
            
            bonds_to_switch.append({
                'bond_index': bond_idx,
                'current_stereo': info['structure'],
                'target_stereo': info['original'],  
                'bond_atoms': info['bond_atoms'],
                'needs_correction': True
            })
    
    return bonds_to_switch


def _get_orca_executable():
    """Get ORCA executable path with fallback strategy."""
    
    orca_path = os.environ.get('ORCA_PATH')
    if orca_path:
        if os.path.isdir(orca_path):
            orca_exe = os.path.join(orca_path, 'orca')
        else:
            orca_exe = orca_path
            
        if os.path.isfile(orca_exe) and os.access(orca_exe, os.X_OK):
            return orca_exe
    
    orca_exe = shutil.which('orca')
    if orca_exe:
        return orca_exe
    
    common_paths = [
        '/opt/orca/orca',
        '/usr/local/bin/orca',
        '/home/orca/orca_6_1_0/orca'
    ]
    
    for path in common_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    
    raise FileNotFoundError("ORCA executable not found. Please set ORCA_PATH environment variable or add ORCA to PATH")



def _update_molecule_coordinates(mol, new_coords):
    """
    Update molecule coordinates from ORCA result and restore original atoms.
    
    Parameters:
        mol (rdkit.Chem.rdchem.Mol): Original molecule
        new_coords (list): New coordinates from ORCA
        
    Returns:
        rdkit.Chem.rdchem.Mol: Updated molecule with new coordinates
    """
    try:
        new_mol = Chem.Mol(mol)
                   

        conf = new_mol.GetConformer()
        
        for i, coord_line in enumerate(new_coords):
            parts = coord_line.split()
            if len(parts) >= 4:  
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                conf.SetAtomPosition(i, (x, y, z))
        
        return new_mol
        
    except Exception as e:
        print(f"Error updating molecule coordinates: {e}")
        return mol

def prepare_for_orca_switching(results, bond_index, target_stereochemistry, print_level=1):
    """
    Prepare molecule and parameters for ORCA stereochemistry switching.
    
    Parameters:
        results (dict): Results from process_smiles()
        bond_index (int): Index of bond to switch
        target_stereochemistry (str): 'cis' or 'trans'
        print_level (int): Logging level
        
    Returns:
        dict: ORCA preparation data including coordinates, bond info, and constraints
    """
    if not results['ready_for_orca']:
        _log("Molecule not ready for ORCA switching", level=1, print_level=print_level)
        return None
    
    mol = results['molecule']
    if not mol:
        return None
    
    # Find the specified bond in bonds that need switching
    target_bond = None
    for bond_info in results['bonds_to_switch']:
        if bond_info['bond_index'] == bond_index:
            target_bond = bond_info
            break
    
    if not target_bond:
        _log(f"Bond {bond_index} is not switchable", level=1, print_level=print_level)
        return None
    
    # Generate ORCA input preparation data
    orca_data = {
        'xyz_coordinates': Chem.MolToXYZBlock(mol),
        'bond_to_switch': {
            'index': bond_index,
            'atoms': target_bond['bond_atoms'],
            'current_stereo': target_bond['current_stereo'],
            'target_stereo': target_stereochemistry
        },
        'molecular_formula': Chem.rdMolDescriptors.CalcMolFormula(mol),
        'charge': Chem.rdmolops.GetFormalCharge(mol),
        'multiplicity': 1  # Assuming singlet, should be calculated properly
    }
    
    _log(f"Prepared ORCA data for bond {bond_index} switching to {target_stereochemistry}", level=1, print_level=print_level)
    return orca_data


def _run_orca_dihedral_rotation(mol, bond_index, target_stereo, n_cores=1, print_level=1):
    """
    Run ORCA calculation with dihedral rotation to switch stereochemistry.
    
    Parameters:
        mol (rdkit.Chem.rdchem.Mol): RDKit molecule with 3D coordinates
        bond_index (int): Index of double bond to switch
        target_stereo (str): Target stereochemistry ('cis' or 'trans')
        n_cores (int): Number of cores for ORCA calculation
        print_level (int): Logging level
        
    Returns:
        dict: Results with corrected molecule and success status
    """
    
    try:
        orca_exe = _get_orca_executable()
        _log(f"Using ORCA executable: {orca_exe}", level=2, print_level=print_level)
        
        bond = mol.GetBondWithIdx(bond_index)
        atom1_idx = bond.GetBeginAtomIdx()
        atom2_idx = bond.GetEndAtomIdx()
        
        atom1 = mol.GetAtomWithIdx(atom1_idx)
        atom2 = mol.GetAtomWithIdx(atom2_idx)
        
        neighbors1 = [n for n in atom1.GetNeighbors() if n.GetIdx() != atom2_idx]
        neighbors2 = [n for n in atom2.GetNeighbors() if n.GetIdx() != atom1_idx]
        
        if not neighbors1 or not neighbors2:
            return {'success': False, 'message': 'Bond atoms missing neighbors for dihedral definition'}
        
        neighbors1.sort(key=lambda x: int(x.GetProp("_CIPRank")) if x.HasProp("_CIPRank") else 0, reverse=False)
        neighbors2.sort(key=lambda x: int(x.GetProp("_CIPRank")) if x.HasProp("_CIPRank") else 0, reverse=False)
        
        dihedral_atom1 = neighbors1[0].GetIdx()
        dihedral_atom4 = neighbors2[0].GetIdx()
        
        conf = mol.GetConformer()
        current_dihedral = rdMolTransforms.GetDihedralDeg(conf, dihedral_atom1, atom1_idx, atom2_idx, dihedral_atom4)
        target_dihedral = current_dihedral + 160.0  #
        
        _log(f"Dihedral atoms: {dihedral_atom1}-{atom1_idx}-{atom2_idx}-{dihedral_atom4}", level=2, print_level=print_level)
        _log(f"Current dihedral: {current_dihedral:.1f}°, target: {target_dihedral:.1f}°", level=2, print_level=print_level)
        
        
        molecular_charge = Chem.rdmolops.GetFormalCharge(mol)
        
        xyz_block = Chem.MolToXYZBlock(mol)
        
        work_dir = "tmp_strainedSMILES2xyz"
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
        
        input_file = os.path.join(work_dir, "dihedral_scan.inp")
        xyz_file = os.path.join(work_dir, "molecule.xyz")
        
        with open(xyz_file, 'w') as f:
            f.write(xyz_block)
        
        orca_input = f"""# ORCA input for dihedral rotation
! XTBFF opt
%pal nprocs {n_cores} end

%geom
  Scan
    D {dihedral_atom1} {atom1_idx} {atom2_idx} {dihedral_atom4} = {current_dihedral:.1f}, {target_dihedral:.1f}, 35
  end
end

* xyzfile {molecular_charge} 1 molecule.xyz
"""
        
        with open(input_file, 'w') as f:
            f.write(orca_input)
        
        _log(f"Running ORCA dihedral scan with {n_cores} cores in {work_dir}", level=1, print_level=print_level)
        
        result = subprocess.run(
            [orca_exe, "dihedral_scan.inp"],
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=600 
        )
        
        if result.returncode != 0:
            return {
                'success': False, 
                'message': f'ORCA calculation failed: {result.stderr}',
                'corrected_molecule': mol
            }
        
        final_geom_file = os.path.join(work_dir, "dihedral_scan.xyz")
        
        if not os.path.exists(final_geom_file):
            return {
                'success': False, 
                'message': f'ORCA final geometry file not found: {final_geom_file}',
                'corrected_molecule': mol
            }
        
        with open(final_geom_file, 'r') as f:
            xyz_lines = f.readlines()
        
        if len(xyz_lines) < 2:
            return {
                'success': False, 
                'message': 'Invalid XYZ file format',
                'corrected_molecule': mol
            }
        
        n_atoms = int(xyz_lines[0].strip())
        coord_lines = xyz_lines[2:2+n_atoms]  
        corrected_mol = _update_molecule_coordinates(mol, coord_lines)
        
        return {
            'success': True,
            'message': f'Stereochemistry successfully switched to {target_stereo}',
            'corrected_molecule': corrected_mol,
            'orca_output': result.stdout
        }
        
    except FileNotFoundError as e:
        return {
            'success': False, 
            'message': f'ORCA executable not found: {e}',
            'corrected_molecule': mol
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False, 
            'message': 'ORCA calculation timed out',
            'corrected_molecule': mol
        }
    except Exception as e:
        return {
            'success': False, 
            'message': f'ORCA calculation error: {str(e)}',
            'corrected_molecule': mol
        }


def apply_orca_corrections(results, print_level=1, n_cores=1):
    """
    Apply ORCA corrections to all bonds that need switching.
    
    Parameters:
        results (dict): Results from process_smiles()
        print_level (int): Logging level
        n_cores (int): Number of cores for ORCA calculations
        
    Returns:
        dict: Updated results with corrected molecule
    """
    if not results['ready_for_orca'] or not results['bonds_to_switch']:
        _log("No ORCA corrections needed", level=1, print_level=print_level)
        return results
    
    _log(f"Applying ORCA corrections to {len(results['bonds_to_switch'])} bonds", level=1, print_level=print_level)
    
    corrected_results = results.copy()
    corrected_mol = Chem.Mol(results['molecule'])  
    orca_corrections = []
    
    for bond_info in results['bonds_to_switch']:
        bond_index = bond_info['bond_index']
        target_stereo = bond_info['target_stereo']
        
        _log(f"Processing bond {bond_index} ({bond_info['current_stereo']} → {target_stereo})", level=1, print_level=print_level)
        
        orca_result = _run_orca_dihedral_rotation(corrected_mol, bond_index, target_stereo, n_cores, print_level)
        
        if orca_result['success']:
            corrected_mol = orca_result['corrected_molecule']
            _log(f"Successfully corrected bond {bond_index}", level=1, print_level=print_level)
        else:
            _log(f"Failed to correct bond {bond_index}: {orca_result['message']}", level=1, print_level=print_level)
        
        orca_corrections.append({
            'bond_index': bond_index,
            'target_stereochemistry': target_stereo,
            'orca_result': orca_result
        })

    _log("Verifying ORCA corrections...", level=1, print_level=print_level)
    verification_info = _check_stereochemistry(corrected_mol, results['original_smiles'], print_level)
    verification_bonds = _identify_bonds_to_switch(verification_info)
    
    success_count = len(results['bonds_to_switch']) - len(verification_bonds)
    _log(f"ORCA corrections completed: {success_count}/{len(results['bonds_to_switch'])} bonds successfully corrected", level=1, print_level=print_level)
    
    corrected_results['molecule'] = corrected_mol
    corrected_results['stereochemistry_info'] = verification_info
    corrected_results['bonds_to_switch'] = verification_bonds
    corrected_results['ready_for_orca'] = len(verification_bonds) > 0
    corrected_results['orca_corrections'] = orca_corrections
    corrected_results['orca_applied'] = True
    
    return corrected_results


def strainedSMILES2xyz(smiles, print_level=1, no_chirality_enforced_allowed=True, use_orca_corrections=False, n_cores=1):
    """
    Main function: Convert SMILES to 3D molecule with correct stereochemistry.
    
    This is the primary function that returns the corrected RDKit molecule.
    If stereochemistry corrections are needed, they can be applied using ORCA.
    
    Parameters:
        smiles (str): Input SMILES string
        print_level (int): Logging verbosity (0=none, 1=basic, 2=detailed)
        no_chirality_enforced_allowed (bool): Allow conformer generation without chirality
        use_orca_corrections (bool): Apply ORCA corrections for stereochemistry mismatches
        n_cores (int): Number of cores for ORCA calculations (default: 1)
    
    Returns:
        tuple: (mol, correction_info)
            mol (rdkit.Chem.rdchem.Mol): RDKit molecule with 3D coordinates
            correction_info (dict): Information about stereochemistry corrections and ORCA results
    """
    results = process_smiles(smiles, print_level, no_chirality_enforced_allowed)
    
    if use_orca_corrections and results['ready_for_orca']:
        results = apply_orca_corrections(results, print_level, n_cores)
    
    mol = results['molecule']
    
    correction_info = {
        'status': results['status'],
        'stereochemistry_matches': len(results['bonds_to_switch']) == 0,
        'bonds_needing_correction': results['bonds_to_switch'],
        'ready_for_orca': results['ready_for_orca'],
        'stereochemistry_details': results['stereochemistry_info'],
        'orca_applied': results.get('orca_applied', False),
        'orca_corrections': results.get('orca_corrections', [])
    }
    
    if print_level >= 1:
        if correction_info['stereochemistry_matches']:
            print(f"✓ Stereochemistry matches original SMILES")
        else:
            print(f"⚠ {len(results['bonds_to_switch'])} bond(s) need stereochemistry correction")
            for bond_info in results['bonds_to_switch']:
                print(f"  Bond {bond_info['bond_index']}: {bond_info['current_stereo']} → {bond_info['target_stereo']}")
            
            if use_orca_corrections and correction_info['orca_applied']:
                orca_success = sum(1 for corr in correction_info['orca_corrections'] if corr['orca_result']['success'])
                print(f"✓ ORCA corrections applied: {orca_success}/{len(correction_info['orca_corrections'])} successful")
            elif correction_info['ready_for_orca']:
                print(f"💡 Use use_orca_corrections=True to automatically fix stereochemistry")


    
    return mol, correction_info


__all__ = ["strainedSMILES2xyz"]

def mol_to_xyz(mol):
    conf = mol.GetConformer()
    atoms = mol.GetAtoms()
    lines = [str(mol.GetNumAtoms()), "generated by strainedSMILES2xyz"]
    for atom in atoms:
        pos = conf.GetAtomPosition(atom.GetIdx())
        lines.append(f"{atom.GetSymbol()} {pos.x:.6f} {pos.y:.6f} {pos.z:.6f}")
    return "\n".join(lines)


def main():
    import sys
    import math
    if len(sys.argv) < 2:
        print("Usage: python -m strainedsmiles2xyz <SMILES>", file=sys.stderr)
        sys.exit(1)
    smiles = sys.argv[1]
    cores = math.ceil(multiprocessing.cpu_count() / 2)
    mol = strainedSMILES2xyz(smiles, print_level=0, use_orca_corrections=True, n_cores=cores)[0]
    print(mol_to_xyz(mol))


if __name__ == "__main__":
    main()
