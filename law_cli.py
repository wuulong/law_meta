import argparse
import os
from law_processor import LawProcessor
from law_metadata_manager import LawMetadataManager
from dotenv import load_dotenv




def main():
    parser = argparse.ArgumentParser(description='Law Data Management CLI Tool')

    # Group for import/update operations
    group_import_update = parser.add_argument_group('Import/Update Operations')
    group_import_update.add_argument('-x', '--import-xml', type=str,
                                     help='Path to a single XML file containing law data to import.')
    group_import_update.add_argument('-s', '--update-summary', type=str,
                                     help='Path to a file containing multiple law summaries to update.')
    group_import_update.add_argument('-k', '--update-keywords', type=str,
                                     help='Path to a CSV file containing law names and keywords to update (e.g., data/keywords_law.csv).')
    group_import_update.add_argument('-g', '--generate-meta-list', type=str,
                                     help='Path to a file containing a list of law names and Markdown file paths to generate metadata from.')
    group_import_update.add_argument('-m', '--import-meta-list', type=str,
                                     help='Path to a file containing a list of law names to import their generated metadata into the database.')

    # Group for delete operations
    group_delete = parser.add_argument_group('Delete Operations')
    group_delete.add_argument('-d', '--delete-law-list', type=str,
                                  help='Path to a file containing a list of law names to delete all data for.')

    # Group for export operations
    group_export = parser.add_argument_group('Export Operations')
    group_export.add_argument('-e', '--export-law-list', type=str,
                                  help='Path to a file containing a list of law names to export as Markdown.')
    group_export.add_argument('--output-dir', type=str, default='./output',
                                  help='Output directory for exported Markdown files. (Default: ./output)')

    # Group for integrity check
    group_check = parser.add_argument_group('Integrity Check')
    group_check.add_argument('-c', '--check-integrity', action='store_true',
                                 help='Perform a database integrity check and output a report.')

    args = parser.parse_args()
    #print(f"Parsed arguments: {args}")

    law_processor = LawProcessor(db_config)
    law_metadata_manager = LawMetadataManager(db_config, gemini_api_key)

    if args.import_xml:
        law_processor.import_xml(args.import_xml)
    elif args.update_summary:
        law_processor.update_summary(args.update_summary)
    elif args.update_keywords:
        law_processor.update_keywords(args.update_keywords)
    elif args.generate_meta_list:
        law_metadata_manager.generate_meta_list(args.generate_meta_list)
    elif args.import_meta_list:
        law_metadata_manager.load_meta_data_list_to_db(args.import_meta_list)
    elif args.delete_law_list:
        law_processor.delete_law_list(args.delete_law_list)
    elif args.export_law_list:
        law_processor.export_law_list(args.export_law_list, args.output_dir)
    elif args.check_integrity:
        law_processor.check_integrity()
    else:
        parser.print_help()

load_dotenv()

# Database configuration (replace with your actual database details or environment variables)
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'lawdb'),
    'user': os.getenv('DB_USER', 'lawuser'),
    'password': os.getenv('DB_PASSWORD', 'lawpassword'),
    'port': os.getenv('DB_PORT', '5432')
}
#print(f"Database configuration: {db_config}")

# Gemini API Key (replace with your actual API key or environment variable)
gemini_api_key = os.getenv('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY')

if __name__ == '__main__':
    main()
