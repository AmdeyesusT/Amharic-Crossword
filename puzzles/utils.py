from pycrossword import generate_crossword
from .models import Puzzle, Clue
from django.db import transaction
from django.utils import timezone

def generate_amharic_puzzle(title, word_data, user, grid_size=15):
    """
    word_data: {'አበበ': 'የወንድ ስም', ...}
    """
    words = list(word_data.keys())
    
    # 1. Initialize and generate
    # Increase the '5000' (attempts) if you have very long Amharic words
    result = generate_crossword(words, grid_size, grid_size)

    # 2. Safety Check: Did it actually place any words?
    if not result:
        return None 
    
    # print(result)
    # 3. Use a Transaction (Atomic)
    # This ensures that if the code crashes halfway, it doesn't leave a partial puzzle
    actual_placements = result[1]
    with transaction.atomic():
        new_puzzle = Puzzle.objects.create(
            title=title,
            difficulty='medium',
            created_by=user,
            grid_data={
                "width": grid_size,
                "height": grid_size,
                "total_words": len(result[1])
            },
            release_date=timezone.now()
        )

        for placement in actual_placements:
            word_text = placement[0]
            col_val   = placement[1]
            row_val   = placement[2]
            is_horiz   = placement[3]
            # We use .get() just in case to avoid KeyError
            clue_text = word_data[word_text]
            
            Clue.objects.create(
                puzzle=new_puzzle,
                clue_text=clue_text[0] + clue_text[1],
                answer=word_text,
                x_coord=col_val,
                y_coord=row_val,
                # Mapping the library's strings to your 'H'/'V' choices
                direction='H' if is_horiz else 'V',
            )
            
    return new_puzzle