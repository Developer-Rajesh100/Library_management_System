from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


########## Category Model ##########
class Category(models.Model):
    category = models.CharField(
        max_length=50, unique=True, db_index=True, primary_key=True)

    def __str__(self):
        return f"{self.category}"


########## Book Model ##########
class Book(models.Model):
    isbn = models.CharField(max_length=13, unique=True,
                            primary_key=True, db_index=True)
    img = models.ImageField(upload_to='upload/')
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    remaining = models.IntegerField(default=0)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.book_title} | {self.book_category}"


########## Borrow Model ##########
class Borrow(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    borrowing_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.book.title}"


class Book_Borrow(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowing = models.ManyToManyField(Borrow)
    times_borrowed = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.book.title} | {self.times_borrowed}"

########## Review Model ##########


class Review(models.Model):
    book = models.ForeignKey(
        'Book', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure one review per user per book
        unique_together = ['book', 'user']

    def __str__(self):
        return f"{self.book.title} | {self.user.username}"


class Book_Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    review = models.ManyToManyField(Review)
    total_rating = models.IntegerField(default=0)
    total_review = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.book.title} | {self.total_rating} | {self.total_review}"
