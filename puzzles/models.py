from django.db import models

# use this collation "am-ET-x-icu" 
# ex: SELECT * FROM your_table ORDER BY your_column COLLATE "am-ET-x-icu";

class WordBank(models.Model):
    word = models.CharField(max_length=100)
    clue_hint = models.TextField()
    category = models.CharField(max_length=50, db_index=True)

    def __str__(self):
        return self.word

class Puzzle(models.Model):
    DIFFICULTY_CHOICES = [('Easy', 'ቀላል'), ('Medium', 'መካከለኛ'), ('Hard', 'ከባድ')]
    
    title = models.CharField(max_length=200)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    
    grid_data = models.JSONField(help_text="The generated grid layout and solution mapping")
    
    release_date = models.DateField(unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.release_date}"

class Clue(models.Model):
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE, related_name='clues')
    clue_text = models.TextField()
    answer = models.CharField(max_length=100)
    
    x_coord = models.IntegerField()
    y_coord = models.IntegerField()
    direction = models.CharField(max_length=10, choices=[('Across', 'አግድም'), ('Down', 'ቁልቁል')])

    def __str__(self):
        return f"{self.direction}: {self.clue_text[:20]}..."