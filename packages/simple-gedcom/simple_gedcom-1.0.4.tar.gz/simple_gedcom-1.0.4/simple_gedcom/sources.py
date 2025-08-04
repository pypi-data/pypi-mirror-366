from typing import List
from .parser import GedcomParser

def get_source_list(parser: GedcomParser) -> List[dict]:
    """Get all source records as dictionaries"""
    sources_dict = parser.get_sources()
    
    sources_list = []
    for source in sources_dict.values():
        source_data = {
            'Source ID': source.get_pointer(),
            'Title': source.get_title(),
            'Author': source.get_author(),
            'Publication': source.get_publication(),
            'Repository': source.get_repository()
        }
        sources_list.append(source_data)
    
    return sources_list

def save_source_list_to_csv(parser: GedcomParser, output_filename: str = None) -> str:
    """Get source data and save to CSV file"""
    import csv
    import os
    
    # Get the original GEDCOM file path from parser
    gedcom_filepath = parser.get_file_path()
    if gedcom_filepath is None:
        raise ValueError("No GEDCOM file has been parsed yet")
    
    # If no output filename specified, use the GEDCOM file's path and name
    if output_filename is None:
        directory = os.path.dirname(gedcom_filepath)
        base_name = os.path.splitext(os.path.basename(gedcom_filepath))[0]
        output_filename = os.path.join(directory, f"{base_name}_sources.csv")
    
    # Get the source data
    sources = get_source_list(parser)
    
    # Handle empty data
    if not sources:
        # Create empty CSV file
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            pass
        return output_filename
    
    # Get column headers from the first record
    headers = list(sources[0].keys())
    
    # Write to CSV
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(sources)
    
    return output_filename


def get_person_source_list(parser: GedcomParser) -> List[dict]:
    """Get people data with one row per person-source combination"""
    person_source_list = []

    # Go through all individuals
    for person in parser.get_individuals().values():
        pointer = person.get_pointer()
        first_name, last_name = person.get_name()

        # Base person data
        base_person_data = {
            'Person ID': pointer,
            'First Name': first_name,
            'Last Name': last_name          
        }

        person_sources = person.get_all_person_sources()

        if person_sources:
            # Create one row per source
            for source_pointer in person_sources:
                sources_dict = parser.get_sources()
                if source_pointer in sources_dict:
                    source = sources_dict[source_pointer]
                    row_data = base_person_data.copy()
                    row_data.update({
                        'Source ID': source.get_pointer(),
                        'Source Title': source.get_title(),
                        'Source Author': source.get_author(),
                        'Source Publication': source.get_publication(),
                        'Source Repository': source.get_repository()
                    })
                    person_source_list.append(row_data)

    return person_source_list

def save_person_source_list_to_csv(parser: GedcomParser, output_filename: str = None) -> str:
    """Get person source data and save to CSV file"""
    import csv
    import os
    
    # Get the original GEDCOM file path from parser
    gedcom_filepath = parser.get_file_path()
    if gedcom_filepath is None:
        raise ValueError("No GEDCOM file has been parsed yet")
    
    # If no output filename specified, use the GEDCOM file's path and name
    if output_filename is None:
        directory = os.path.dirname(gedcom_filepath)
        base_name = os.path.splitext(os.path.basename(gedcom_filepath))[0]
        output_filename = os.path.join(directory, f"{base_name}_person_sources.csv")
    
    # Get the source data
    person_source_list = get_person_source_list(parser)
    
    # Handle empty data
    if not person_source_list:
        # Create empty CSV file
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            pass
        return output_filename
    
    # Get column headers from the first record
    headers = list(person_source_list[0].keys())
    
    # Write to CSV
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(person_source_list)
    
    return output_filename