from packaging import version
from typing import Union

def check_version(installed_version: str, version_spec: str) -> bool:
    """
    Vérifie rigoureusement qu'une version satisfait une spécification.
    
    Args:
        installed_version: Version installée (ex: '1.2.3')
        version_spec: Spécification de version (ex: '>=1.0,<2.0 || 2.5.0')
    
    Returns:
        bool: True si la version est compatible
    """
    try:
        installed_ver = version.parse(installed_version)
        version_spec = version_spec.strip()
        
        if not version_spec:  # Aucune spécification = tout est accepté
            return True
            
        # Gestion des OU logiques (||)
        if '||' in version_spec:
            return any(
                _process_spec(installed_ver, part.strip())
                for part in version_spec.split('||')
            )
        
        return _process_spec(installed_ver, version_spec)
    except Exception as e:
        raise ValueError(f"Version check failed for '{installed_version}' with spec '{version_spec}': {str(e)}")

def _process_spec(ver: version.Version, spec: str) -> bool:
    """Traite une spécification individuelle (peut contenir des ET)"""
    # Gestion des ET logiques (&&)
    if '&&' in spec:
        return all(
            _compare(ver, part.strip())
            for part in spec.split('&&')
        )
    
    # Gestion des intervalles avec virgule
    if ',' in spec:
        parts = [p.strip() for p in spec.split(',')]
        if len(parts) == 2:
            return (_compare(ver, f'>={parts[0]}') and 
                    _compare(ver, f'<={parts[1]}'))
    
    return _compare(ver, spec)

def _compare(ver: version.Version, spec: str) -> bool:
    """Compare une version avec une spécification individuelle"""
    spec = spec.strip()
    
    # Détection de l'opérateur
    op = ''
    if spec.startswith(('>=', '<=', '==', '!=')):
        op = spec[:2]
        spec_ver = version.parse(spec[2:].strip())
    elif spec.startswith(('>', '<', '~', '^')):
        op = spec[0]
        spec_ver = version.parse(spec[1:].strip())
    else:
        # Version exacte si pas d'opérateur
        return ver == version.parse(spec)
    
    # Comparaisons
    if op == '>':
        return ver > spec_ver
    elif op == '>=':
        return ver >= spec_ver
    elif op == '<':
        return ver < spec_ver
    elif op == '<=':
        return ver <= spec_ver
    elif op == '==':
        return ver == spec_ver
    elif op == '!=':
        return ver != spec_ver
    elif op == '~':  # Compatible release (pip style)
        return ver >= spec_ver and ver < version.parse(f"{spec_ver.major}.{spec_ver.minor + 1}.0")
    elif op == '^':  # Caret requirement (npm style)
        if spec_ver.major > 0:
            return ver >= spec_ver and ver < version.parse(f"{spec_ver.major + 1}.0.0")
        elif spec_ver.minor > 0:
            return ver >= spec_ver and ver < version.parse(f"0.{spec_ver.minor + 1}.0")
        else:
            return ver >= spec_ver and ver < version.parse(f"0.0.{spec_ver.micro + 1}")
    
    return False