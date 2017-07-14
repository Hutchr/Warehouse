from django.db import models

# Create your models here.

class NewsLetterEmail(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class NewsLetterUser(models.Model):
    title = models.ForeignKey(NewsLetterEmail, unique=True)
    def __str__(self):
        return self.title

class Contact(models.Model):
    first_name = models.CharField(max_length=50, verbose_name='Όνομα')
    last_name = models.CharField(max_length=50, verbose_name='Επίθετο')
    email = models.EmailField()
    subject = models.CharField(max_length=50, verbose_name='Θέμα')
    message = models.TextField(verbose_name='Μήνυμα')
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='Ημερομηνία Αποστολής')
    is_readed = models.BooleanField(default=False, verbose_name='Διαβασμένο')

    class Meta:
        ordering = ['date_created']
        verbose_name_plural = 'Μηνύματα Επικοινωνίας'
    def __str__(self):
        return self.subject