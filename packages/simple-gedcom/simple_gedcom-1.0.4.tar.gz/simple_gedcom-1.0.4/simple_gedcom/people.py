from typing import List
from .parser import GedcomParser
from .elements import Person 

def fill_person(parser: GedcomParser, person: Person) -> dict:
    """Fill person data dictionary"""
    
    first_name, last_name = person.get_name()
    
    birth_date, birth_place = person.get_birth_date_place()
    death_date, death_place = person.get_death_date_place()
    
    return {
        'Person ID': person.get_pointer(),
        'First Name': first_name,
        'Last Name': last_name,
        'Birth Date': birth_date,
        'Birth Place': birth_place,
        'Death Date': death_date,
        'Death Place': death_place
    }

def get_person_list(parser: GedcomParser) -> List[dict]:
    """Get people data with one row per person"""
    person_list = []

    # Go through all individuals
    for person in parser.get_individuals().values():

        person_data = fill_person(parser, person)

        person_list.append(person_data)

    return person_list

def find_persons_by_name(parser: GedcomParser, first_name: str = None, last_name: str = None) -> list:
    """Find persons by first and/or last name"""
    if first_name is None and last_name is None:
        # If no search criteria provided, return all persons
        return get_person_list(parser)
    
    person_list = get_person_list(parser)
    matched_persons = []
    
    for person in person_list:
        match = True
        
        # Check first name if provided
        if first_name is not None:
            person_first_name = person.get('First Name', '').strip()
            if first_name.lower() not in person_first_name.lower():
                match = False
        
        # Check last name if provided
        if last_name is not None:
            person_last_name = person.get('Last Name', '').strip()
            if last_name.lower() not in person_last_name.lower():
                match = False
        
        if match:
            matched_persons.append(person)
    
    return matched_persons

def get_pedigree(parser: GedcomParser, person_pointer: str = None) -> dict:
    """Get pedigree starting from a specific person or the first person found"""    
    root_child_elements = parser.get_root_child_elements()
    pedigree = {}
    
    if person_pointer:
        # Find the specific person by pointer
        for element in root_child_elements:
            if isinstance(element, Person) and element.get_pointer() == person_pointer:
                start_person = element
                break
        
        if start_person is None:
            raise ValueError(f"Person with pointer '{person_pointer}' not found")
    else:    
        # Use the first person found (Home Person)
        for element in root_child_elements:
            if isinstance(element, Person):
                start_person = element
                break

    # If we found a person (either specified or first one), build the pedigree
    if start_person is not None:
        # Start with the specified person as HP (Home Person)
        hp_data = fill_person(parser, start_person)
        hp_data['Generation'] = 1
        pedigree["HP"] = hp_data
                
        # Recursively build the pedigree
        build_pedigree_recursive(parser, element, 1, 1, 10, pedigree)
        
    return pedigree

def build_pedigree_recursive(parser: GedcomParser, person: Person, position_number: int, generation: int, max_generations: int, pedigree: dict):
    """Recursively build pedigree up to max_generations"""
    
    # Stop if we've reached the maximum generation
    if generation > max_generations:
        return
    
    # Get father and mother
    father, mother = parser.get_father_mother(person)
    
    # Calculate positions for next generation (binary tree numbering)
    father_position = position_number * 2
    mother_position = position_number * 2 + 1
    
    # Generate the position keys based on generation
    father_key = get_position_key(father_position, generation)
    mother_key = get_position_key(mother_position, generation)
    
    # Process father
    if father is not None:
        father_data = fill_person(parser, father)
        father_data['Generation'] = generation + 1
        pedigree[father_key] = father_data
        build_pedigree_recursive(parser, father, father_position, generation + 1, max_generations, pedigree)
    
    # Process mother
    if mother is not None:
        mother_data = fill_person(parser, mother)
        mother_data['Generation'] = generation + 1
        pedigree[mother_key] = mother_data
        build_pedigree_recursive(parser, mother, mother_position, generation + 1, max_generations, pedigree)

def get_position_key(position_number: int, generation: int) -> str:
    """Generate position key based on generation and position number"""
    if generation == 1:  # Parents
        return "P1" if position_number == 2 else "P2"
    elif generation == 2:  # Grandparents
        # Position 4,5,6,7 -> GP1,GP2,GP3,GP4
        return f"GP{position_number - 3}"
    else:  # Great-grandparents and beyond
        # Generate G prefix (G, GG, GGG, etc.)
        g_count = generation - 2
        g_prefix = "G" * g_count
        
        # Calculate the starting position for this generation
        # Gen 3: starts at position 8, Gen 4: starts at position 16, etc.
        generation_start = 2 ** generation
        relative_position = position_number - generation_start + 1
        
        return f"{g_prefix}GP{relative_position}"

def save_person_list_to_csv(parser: GedcomParser, output_filename: str = None) -> str:
    """Get people data and save to CSV file"""
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
        output_filename = os.path.join(directory, f"{base_name}.csv")
    
    # Get the people data
    person_list = get_person_list(parser)
    
    # Handle empty data
    if not person_list:
        # Create empty CSV file
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            pass
        return output_filename
        
    # Get column headers from the first record
    headers = list(person_list[0].keys())
    
    # Write to CSV
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(person_list)
    
    return output_filename

def save_pedigree_to_csv(parser: GedcomParser, output_filename: str = None) -> str:
    """Get pedigree data and save to CSV file"""
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
        output_filename = os.path.join(directory, f"{base_name}_pedigree.csv")
    
    # Get the pedigree data
    pedigree = get_pedigree(parser)
    
    # Handle empty data
    if not pedigree:
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            pass
        return output_filename
        
    # Transform the data (equivalent to DataFrame.T.reset_index())
    # Assuming pedigree is a dict where keys become the 'Position' column
    pedigree_list = []
    for position, data in pedigree.items():
        # Create a new dict with Position as first field
        row = {'Position': position}
        # Add all other fields from the data
        if isinstance(data, dict):
            row.update(data)
        else:
            # If data is not a dict, store it in a 'Value' column
            row['Value'] = data
        pedigree_list.append(row)
    
    # Sort by Generation (assuming Generation is a field in the data)
    if pedigree_list and 'Generation' in pedigree_list[0]:
        pedigree_list.sort(key=lambda x: x.get('Generation', 0))
    
    # Get headers
    if pedigree_list:
        headers = list(pedigree_list[0].keys())
    else:
        headers = ['Position']
    
    # Write to CSV
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(pedigree_list)
    
    return output_filename
