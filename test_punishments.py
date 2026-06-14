"""Test script to verify punishment logging system"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from di import Container
from infrastructure.logging import get_logger

logger = get_logger(__name__)


async def test_punishment_system():
    """Test the punishment logging system"""
    try:
        # Initialize container
        logger.info("Initializing container...")
        container = Container()
        
        # Get services
        logger.info("Getting admin service...")
        admin_service = await container.get_admin_service()
        
        if not admin_service:
            logger.error("Failed to get admin service!")
            return False
        
        logger.info("✅ Admin service initialized successfully")
        
        # Test logging a warning
        logger.info("Testing warning logging...")
        warning_id = await admin_service.log_warning(
            user_id=123456789,
            mod_id=987654321,
            reason="Test warning"
        )
        logger.info(f"✅ Warning logged with ID: {warning_id}")
        
        # Test logging a mute
        logger.info("Testing mute logging...")
        mute_id = await admin_service.log_mute(
            user_id=123456789,
            mod_id=987654321,
            hours=1,
            minutes=0,
            reason="Test mute"
        )
        logger.info(f"✅ Mute logged with ID: {mute_id}")
        
        # Test logging a kick
        logger.info("Testing kick logging...")
        kick_id = await admin_service.log_kick(
            user_id=123456789,
            mod_id=987654321,
            reason="Test kick"
        )
        logger.info(f"✅ Kick logged with ID: {kick_id}")
        
        # Test getting violations
        logger.info("Testing violations retrieval...")
        violations = await admin_service.get_user_violations(123456789)
        logger.info(f"✅ Retrieved {len(violations)} violations")
        
        # Test getting violation count
        logger.info("Testing violation count...")
        count = await admin_service.get_violation_count(123456789)
        logger.info(f"✅ User has {count} total violations")
        
        # Test getting violations summary
        logger.info("Testing violations summary...")
        summary = await admin_service.get_violations_summary(123456789)
        logger.info(f"✅ Summary: Total={summary['total']}, Active={summary['active']}")
        logger.info(f"   By type: {summary['by_type']}")
        
        # Print all violations
        logger.info("All recorded violations:")
        for violation in violations:
            logger.info(f"  - {violation['type'].upper()}: {violation['reason']} (ID: {violation['id']})")
        
        logger.info("✅ All tests passed!")
        
        # Shutdown
        await container.shutdown()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = asyncio.run(test_punishment_system())
    sys.exit(0 if success else 1)
