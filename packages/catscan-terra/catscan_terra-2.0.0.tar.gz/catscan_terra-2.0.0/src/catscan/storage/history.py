"""Scan history management for CatSCAN."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from catscan.utils import get_logger
logger = get_logger('catscan.storage.history')
from catscan.config import HISTORY_DIR, VERSION


def save_scan_results(org_name: str, workspaces_data: List[Dict], processed_count: int, error_count: int) -> bool:
    """Save scan results to history"""
    logger.info(f"Saving scan results for org: {org_name} ({len(workspaces_data)} workspaces)")
    
    try:
        HISTORY_DIR.mkdir(exist_ok=True)
        logger.debug(f"History directory ensured at: {HISTORY_DIR}")
        
        timestamp = datetime.now()
        scan_data = {
            "timestamp": timestamp.isoformat(),
            "organization": org_name,
            "version": VERSION,
            "workspaces": workspaces_data,
            "summary": {
                "total_workspaces": len(workspaces_data),
                "processed_workspaces": processed_count,
                "error_workspaces": error_count,
                "total_resources": sum(ws.get("resource_count", 0) for ws in workspaces_data)
            }
        }
        
        filename = f"scan_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        scan_file = HISTORY_DIR / filename
        
        logger.debug(f"Writing scan data to: {scan_file}")
        with open(scan_file, 'w') as f:
            json.dump(scan_data, f, indent=2)
        
        logger.info(f"Scan results saved to: {filename}")
        
        # Update scan index
        index_file = HISTORY_DIR / "scans.json"
        scans_index = []
        
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    scans_index = json.load(f)
                logger.debug(f"Loaded existing scan index with {len(scans_index)} entries")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load scan index, starting fresh: {str(e)}")
                scans_index = []
        
        scans_index.append({
            "filename": filename,
            "timestamp": scan_data["timestamp"],
            "organization": org_name,
            "summary": scan_data["summary"]
        })
        
        # Keep only last 30 scans
        original_count = len(scans_index)
        scans_index = scans_index[-30:]
        if original_count > 30:
            logger.info(f"Trimmed scan index from {original_count} to {len(scans_index)} entries")
        
        logger.debug("Updating scan index")
        with open(index_file, 'w') as f:
            json.dump(scans_index, f, indent=2)
        
        cleanup_old_scans(scans_index)
        logger.info("Scan results saved successfully")
        return True
        
    except (IOError, OSError) as e:
        logger.error(f"Failed to save scan results: {str(e)}", exc_info=True)
        return False


def cleanup_old_scans(scans_index: List[Dict]):
    """Remove scan files not in the index"""
    logger.debug("Starting cleanup of old scan files")
    
    try:
        if not HISTORY_DIR.exists():
            logger.debug("History directory does not exist, nothing to clean")
            return
            
        valid_files = {scan["filename"] for scan in scans_index}
        valid_files.add("scans.json")
        logger.debug(f"Valid files to keep: {len(valid_files)}")
        
        removed_count = 0
        for file in HISTORY_DIR.glob("scan_*.json"):
            if file.name not in valid_files:
                logger.debug(f"Removing old scan file: {file.name}")
                file.unlink()
                removed_count += 1
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old scan files")
        else:
            logger.debug("No old scan files to clean up")
                
    except (IOError, OSError) as e:
        logger.error(f"Error during cleanup: {str(e)}")
        pass


def load_scan_history() -> List[Dict]:
    """Load scan history from index"""
    logger.debug("Loading scan history")
    
    try:
        index_file = HISTORY_DIR / "scans.json"
        if not index_file.exists():
            logger.debug("No scan history index found")
            return []
            
        with open(index_file, 'r') as f:
            history = json.load(f)
            logger.info(f"Loaded scan history with {len(history)} entries")
            return history
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse scan history: {str(e)}")
        return []
    except IOError as e:
        logger.error(f"Failed to read scan history: {str(e)}")
        return []


def load_scan_details(filename: str) -> Optional[Dict]:
    """Load details for a specific scan"""
    logger.debug(f"Loading scan details from: {filename}")
    
    try:
        scan_file = HISTORY_DIR / filename
        if not scan_file.exists():
            logger.warning(f"Scan file not found: {filename}")
            return None
            
        with open(scan_file, 'r') as f:
            data = json.load(f)
            logger.info(f"Successfully loaded scan details for {filename}")
            return data
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse scan file {filename}: {str(e)}")
        return None
    except IOError as e:
        logger.error(f"Failed to read scan file {filename}: {str(e)}")
        return None