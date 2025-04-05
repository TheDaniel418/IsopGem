from shared.utils.config import get_config

def main():
    print("Testing IsopGem basic functionality...")
    
    # Load configuration
    config = get_config()
    
    # Print basic configuration information
    print(f"Application name: {config.application.name}")
    print(f"Application version: {config.application.version}")
    print(f"Environment: {os.environ.get('ISOPGEM_ENV', 'development')}")
    
    # Show enabled pillars
    print("\nEnabled Pillars:")
    if config.pillars.gematria.enabled:
        print("- Gematria")
    if config.pillars.geometry.enabled:
        print("- Geometry")
    if config.pillars.document_manager.enabled:
        print("- Document Manager")
    if config.pillars.astrology.enabled:
        print("- Astrology")
    if config.pillars.tq.enabled:
        print("- TQ")
    
    print("\nBasic functionality test completed successfully!")

if __name__ == "__main__":
    import os
    main() 