import csv
import random

# Step 1: import the data.
def import_card_list(filename):
    card_list = []
    try:
        with open(filename, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            print(f"CSV Headers: {headers}")  # Debugging output

            for row in reader:
                try:
                    card = {
                        'name': row['name'],
                        'type': row['type'],
                        'stage': row['stage'],
                        'evolution': row['evolution'] if 'evolution' in row else None,
                        'rarity': row['rarity'],
                        'quantity': int(row['quantity']),
                        'order' : row['order']
                    }
                    for _ in range(card['quantity']):
                        card_list.append(card)
                except KeyError as e:
                    print(f"Missing column in CSV: {e}")
                except ValueError as e:
                    print(f"Invalid data in CSV: {e}")
    except FileNotFoundError:
        print(f"File not found: {filename}")
    return card_list

# Step 2: Ask how many players.
def get_player_count():
    while True:
        try:
            players = int(input("Enter the number of players: "))
            if players > 0:
                return players
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

# Evolution criteria check
def evolution_criteria_met(cube, chosen_card, required_stage):
    required_evolution = chosen_card['evolution']
    if required_stage == 'Stage 1':
        stage1_cards = [card for card in cube if card['stage'] == 'Stage 1']
        return required_evolution in [card['name'] for card in stage1_cards]
    elif required_stage == 'Basic':
        basic_cards = [card for card in cube if card['stage'] == 'Basic']
        return required_evolution in [card['name'] for card in basic_cards]
    return False

# Step 3: Start building cube.
def build_cube(card_list, players):
    cube = []
    packs = []
    required_size = 11 * 4 * players  # 11 cards per pack per player

    while len(cube) < required_size:
        pack = build_pack(card_list, cube)
        packs.append(pack)
        cube.extend(pack)

    return cube, packs

def build_pack(card_list, cube):
    pack = []

    # Add 1 rare card
    rare_cards = [card for card in card_list if card['rarity'] == 'Rare']
    if rare_cards:
        chosen_card = choose_card(rare_cards, card_list, cube, is_pokemon=True)
        if chosen_card:
            pack.append(chosen_card)

    # Add 3 uncommon cards
    for _ in range(3):
        uncommon_cards = [card for card in card_list if card['rarity'] == 'Uncommon']
        if uncommon_cards:
            chosen_card = choose_card(uncommon_cards, card_list, cube, is_pokemon=True)
            if chosen_card:
                pack.append(chosen_card)

    # Add 7 common cards
    for _ in range(7):
        common_cards = [card for card in card_list if card['rarity'] == 'Common']
        if common_cards:
            chosen_card = choose_card(common_cards, card_list, cube, is_pokemon=False)
            if chosen_card:
                pack.append(chosen_card)

    return pack

def choose_card(cards, card_list, cube, is_pokemon=False):
    while cards:
        if is_pokemon:
            weighted_cards = []
            for card in cards:
                if card['stage'] == 'Stage 2':
                    weighted_cards.extend([card] * 3)  # Higher weight for Stage 2
                elif card['stage'] == 'Stage 1':
                    weighted_cards.extend([card] * 2)  # Higher weight for Stage 1
                else:
                    weighted_cards.append(card)
            chosen_card = random.choice(weighted_cards)
        else:
            trainer_cards = [card for card in cards if card['type'] == 'Trainer']
            pokemon_cards = [card for card in cards if card['type'] != 'Trainer']
            if trainer_cards and pokemon_cards:
                chosen_card = random.choices(trainer_cards + pokemon_cards, weights=[0.2] * len(trainer_cards) + [0.8] * len(pokemon_cards))[0]
            elif trainer_cards:
                chosen_card = random.choice(trainer_cards)
            elif pokemon_cards:
                chosen_card = random.choice(pokemon_cards)
            else:
                return None
            
        if chosen_card['type'] == 'Trainer':
            card_list.remove(chosen_card)
            return chosen_card
        else:
            if chosen_card['stage'] == 'Stage 2' and evolution_criteria_met(cube, chosen_card, 'Stage 1'):
                card_list.remove(chosen_card)
                return chosen_card
            elif chosen_card['stage'] == 'Stage 1' and evolution_criteria_met(cube, chosen_card, 'Basic'):
                card_list.remove(chosen_card)
                return chosen_card
            elif chosen_card['stage'] == 'Basic':
                card_list.remove(chosen_card)
                return chosen_card
        cards.remove(chosen_card)
    return None

# Save card list and cube to file
def save_to_file(card_list, cube, packs, card_list_filename='card_list_out.csv', cube_filename='cube_list.csv', packs_filename='packs_list.csv'):
    # Save remaining card list
    with open(card_list_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'type', 'stage', 'evolution', 'rarity', 'quantity', 'order'])
        writer.writeheader()
        card_count = {}
        for card in card_list:
            if card['name'] in card_count:
                card_count[card['name']]['quantity'] += 1
            else:
                card_count[card['name']] = card
                card_count[card['name']]['quantity'] = 1
        for card in card_count.values():
            writer.writerow(card)
    
    # Save cube list
    with open(cube_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'type', 'stage', 'evolution', 'rarity', 'quantity', 'order'])
        writer.writeheader()
        card_count = {}
        for card in cube:
            if card['name'] in card_count:
                card_count[card['name']]['quantity'] += 1
            else:
                card_count[card['name']] = card
                card_count[card['name']]['quantity'] = 1
        for card in card_count.values():
            writer.writerow(card)

    # Save packs list
    with open(packs_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['pack_number', 'name', 'type', 'stage', 'evolution', 'rarity', 'order'])
        for pack_number, pack in enumerate(packs, start=1):
            for card in pack:
                writer.writerow([pack_number, card['name'], card['type'], card['stage'], card['evolution'], card['rarity'], card['order']])

# Main function
if __name__ == "__main__":
    card_list = import_card_list('card_list.csv')
    if not card_list:
        print("No cards were loaded. Please check your CSV file.")
    else:
        players = get_player_count()
        cube, packs = build_cube(card_list, players)
        save_to_file(card_list, cube, packs)
        print("Cube built and saved successfully.")
