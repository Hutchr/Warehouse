from django.db import models
from django.utils import timezone
from inventory_manager.models import *
from decimal import Decimal

# Create your models here.




class Fixed_costs(models.Model):
    # You have to make defaults of Λογαριασμοί, Προσωπικό, Αγορές
    title = models.CharField(max_length=64,unique=True,)
    total_pay = models.DecimalField(decimal_places=2,max_digits=10,default=0, verbose_name='Πιστωτικό Υπόλοιπο')
    total_dept = models.DecimalField(decimal_places=2,max_digits=10,default=0, verbose_name='Χρεωστικό Υπόλοιπο')

    def __str__(self):
        return self.title
        
    def show_remain(self):
        return Decimal(self.total_dept-self.total_pay)
        
    class Meta:
        verbose_name="Κεντρική Κατηγορία Εξόδων   "




class Fixed_Costs_item(models.Model):
    title = models.CharField(max_length=64,unique=True,verbose_name="Ονομασία Κατηγορίας")
    category = models.ForeignKey(Fixed_costs)
    total_pay = models.DecimalField(decimal_places=2, max_digits=10, default=0, verbose_name='Πιστωτικό Υπόλοιπο')
    total_dept = models.DecimalField(decimal_places=2, max_digits=10 ,default=0, verbose_name='Χρεωστικό Υπόλοιπο')

    def show_remain(self):
        return self.total_dept-self.total_pay
        
        
    class Meta:
        verbose_name="Λογαριασμοί και Πάγια έξοδα"
        
        
        
    def __str__(self):
        return self.title






class Order_Fixed_Cost(models.Model):
    # Creates a new payment order, for the specific bill
    CHOICES=(('a','Απλήρωτη'),('b','Πληρώθηκε'))
    title = models.CharField(max_length=64,verbose_name='Αρ.Παραστατικού/Σχολιασμός')
    category = models.ForeignKey(Fixed_Costs_item, verbose_name='Λογαριασμός')
    date = models.DateField(default=timezone.now,verbose_name='Ημερομηνία Λήξης')
    price = models.DecimalField(max_digits=8,decimal_places=2,verbose_name='Ποσό Πληρωμής')
    credit_balance = models.DecimalField(max_digits=8,decimal_places=2, default=0,verbose_name='Πιστωτικό Υπόλοιπο')
    active = models.CharField(max_length=1,choices=CHOICES,default='a')
    payment_method = models.ForeignKey(PaymentMethod, null=True,verbose_name='Τρόπος Πληρωμής')
    class Meta:
        verbose_name="Εντολές Πληρωμών"

    def __str__(self):
        return self.title

    def show_remain(self):
        return self.price-self.credit_balance






class PayOrderFixedCost(models.Model):
    #Creates a receipt for the orders created!
    title = models.CharField(max_length=64,verbose_name='Αρ.Παραστατικού')
    date = models.DateField(default=timezone.now,verbose_name='Ημερομηνία Πληρωμής')
    price = models.DecimalField(max_digits=8,decimal_places=2,verbose_name='Αξία')
    payment_method = models.ForeignKey(PaymentMethod, null=True,verbose_name='Τρόπος Πληρωμής')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name="Αποδείξη Πληρωμής"    







class Occupation(models.Model):
    title = models.CharField(max_length=64,unique=True,verbose_name='Απασχόληση')
    category = models.ForeignKey(Fixed_costs,)
    notes = models.TextField(blank=True, null=True,verbose_name='Σημειώσεις')
    total_cost = models.DecimalField(max_digits=10,decimal_places=2,default=0, verbose_name='Συνολικά Έξοδα')
    remaining_cost = models.DecimalField(max_digits=10,decimal_places=2,default=0, verbose_name='Πιστωτικό Υπόλοιπο')

    class Meta:
        verbose_name="Απασχόληση   "

    def show_remain(self):
        return Decimal(self.total_cost - self.remaining_cost)

    def __str__(self):
        return self.title



class Person(models.Model):
    STATUS_CHOICES =(('a','Ενεργός'),('b','Μη Ενεργός'))
    title = models.CharField(max_length=64,unique=True, verbose_name='Ονοματεπώνυμο')
    phone = models.CharField(max_length=10,verbose_name='Τηλέφωνο', blank=True)
    phone1 = models.CharField(max_length=10, verbose_name='Κινητό', blank=True)
    date_joined = models.DateField(default=timezone.now,verbose_name='Ημερομηνία Πρόσληψης')
    occupation = models.ForeignKey(Occupation, verbose_name='Απασχόληση')

    total_amount_paid = models.DecimalField(max_digits=6,decimal_places=2,default=0,verbose_name='Συνολική Πληρωμή')
    status = models.CharField(default='a', max_length=1, choices=STATUS_CHOICES)

    hour_salary_sum = models.DecimalField(max_digits=6,decimal_places=2,default=0,verbose_name='Υπόλοιπο Υπερωρίων')
    salary_paid = models.DecimalField(max_digits=10,decimal_places=2,default=0, verbose_name='Πιστωτικό Υπόλοιπο')

    class Meta:
        verbose_name="Υπάλληλος   "

    def show_remain(self):
        return self.total_amount_paid - self.salary_paid

        
    def __str__(self):
        return self.title


class PersonHoursCreate(models.Model):
    STATUS_CHOICES =(('a','Ενεργός'),('b','Μη Ενεργός'))
    title = models.CharField(max_length=64,unique=True, verbose_name='Περιγραφή')
    person = models.ForeignKey(Person, verbose_name='Υπάλληλος')
    value = models.DecimalField(max_digits=6,decimal_places=2,default=0, verbose_name='Αξία')
    day_added =  models.DateField(auto_now=timezone.now)
    day_expire =  models.DateField(default=timezone.now, verbose_name='Πληρωμή μέχρι .....')
    status = models.CharField(default='a', max_length=1, choices=STATUS_CHOICES)
    times_per_month = models.DecimalField(max_digits=4,decimal_places=1,default=0,verbose_name='Υπερωρίες')
    hour_salary = models.DecimalField(max_digits=6,decimal_places=2,default=0,verbose_name='Ωρομίσθιο')
    
    class Meta:
        verbose_name="Εντολές Πληρωμών-Not Working"

    def __str__(self):
        return self.title


class PersonHoursPay(models.Model):
    title = models.CharField(max_length=64,unique=True, verbose_name='Περιγραφή')
    person = models.ForeignKey(Person, verbose_name='Υπάλληλος')
    value = models.DecimalField(max_digits=6,decimal_places=2,default=0, verbose_name='Αξία')
    day_added =  models.DateField(auto_now=timezone.now)

    def __str__(self):
        return self.title



class CategoryPersonPay(models.Model):
    # You have to make defaults of Μισθός, IKA/TEBE, Extra,
    title = models.CharField(max_length=60,unique=True)
    total_cost  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    def __str__(self):
        return self.title




class CreatePersonSalaryCost(models.Model):
    STATUS_CHOICES =(('a','Ενεργός'),('b','Μη Ενεργός'))
    title = models.CharField(max_length=64, verbose_name='Περιγραφή')
    person = models.ForeignKey(Person, verbose_name='Υπάλληλος')
    category = models.ForeignKey(CategoryPersonPay, verbose_name='Είδος Πληρωμής')
    value = models.DecimalField(max_digits=8,decimal_places=2,default=0, verbose_name='Αξία')
    day_added =  models.DateField(auto_now=timezone.now)
    day_expire =  models.DateField(default=timezone.now, verbose_name='Πληρωμή μέχρι .....')
    status = models.CharField(default='a', max_length=1, choices=STATUS_CHOICES)
    paid_value = models.DecimalField(max_digits=8,decimal_places=2,default=0, verbose_name='Πιστωτικό Υπόλοιπο')
    payment_method = models.ForeignKey(PaymentMethod, null=True,verbose_name='Τρόπος Πληρωμής')

    class Meta:
        verbose_name="Εντολές Πληρωμής Υπαλλήλων. " 
        
        
    def __str__(self):
        return self.title

    def show_remain(self):
        return self.value -self.paid_value

class PayPersonSalaryCost(models.Model):
    title = models.CharField(max_length=64, verbose_name='Περιγραφή')
    person = models.ForeignKey(Person, verbose_name='Υπάλληλος')
    category = models.ForeignKey(CategoryPersonPay, verbose_name='Είδος Πληρωμής')
    value = models.DecimalField(max_digits=6,decimal_places=2,default=0, verbose_name='Αξία')
    day_added =  models.DateField(auto_now=timezone.now)
    payment_method = models.ForeignKey(PaymentMethod, null=True,verbose_name='Τρόπος Πληρωμής')

    class Meta:
        verbose_name="Αποδείξη Πληρωμής Υπαλλήλων"

    def __str__(self):
        return self.title




#-----------------Agores/Episkeues----------------------------


class Pagia_Exoda(models.Model):
    #Create default of Αγορές, Επισκευές, Διάφορα Έξοδα
    title= models.CharField(max_length=64, unique=True, verbose_name='')
    category = models.ForeignKey(Fixed_costs)
    notes = models.TextField(blank=True, null=True,verbose_name='Σημειώσεις')
    total_cost = models.DecimalField(max_digits=10,decimal_places=2,default=0,verbose_name='Συνολικά Έξοδα')
    remaining_cost = models.DecimalField(max_digits=10,decimal_places=2,default=0,verbose_name='Πιστωτικό Υπόλοιπο')


    def __str__(self):
        return self.title
        
    def show_remain(self):
        return self.total_cost - self.remaining_cost



class PersonMastoras(models.Model):
    title = models.CharField(unique=True,max_length=64,verbose_name="Εταιρία/Ονοματεπώνυμο")
    phone = models.CharField(max_length=10,verbose_name='Τηλέφωνο',blank=True, null=True)
    phone1 = models.CharField(max_length=10, verbose_name='Κινητό',blank=True, null=True)
    occupation = models.CharField(max_length=100, verbose_name="Απασχόληση", blank=True, null=True)

    total_cost = models.DecimalField(max_digits=10,decimal_places=2,default=0,verbose_name='Συνολικά Έξοδα')
    remaining_cost = models.DecimalField(max_digits=10,decimal_places=2,default=0,verbose_name='Πιστωτικό Υπόλοιπο')


    def __str__(self):
        return self.title
        
    def show_remain(self):
        return  self.remaining_cost



class Pagia_Exoda_Order(models.Model):
    CHOICES=(('a','Απλήρωτη'),('b','Πληρώθηκε'))
    title = models.CharField(max_length=64,unique=True,verbose_name='Αρ.Παραστατικού')
    category = models.ForeignKey(Pagia_Exoda, verbose_name='Λογαριασμός')
    person = models.ForeignKey(PersonMastoras,verbose_name='Εταιρία', null=True)
    date = models.DateField(default=timezone.now,verbose_name='Ημερομηνία Λήξης')
    price = models.DecimalField(max_digits=8,decimal_places=2,verbose_name='Αξία')
    credit_balance = models.DecimalField(max_digits=8,decimal_places=2, default=0,verbose_name='Υπόλοιπο')
    active = models.CharField(max_length=1,choices=CHOICES,default='a')
    payment_method = models.ForeignKey(PaymentMethod, null=True,verbose_name='Τρόπος Πληρωμής')


    def __str__(self):
        return self.title

    def show_remain(self):
        return self.price - self.credit_balance

        
class Pagia_Exoda_Pay_Order(models.Model):
    title = models.CharField(max_length=64,unique=True, verbose_name='Περιγραφή')
    person = models.ForeignKey(PersonMastoras, verbose_name='Εταιρία')
    value = models.DecimalField(max_digits=6,decimal_places=2,default=0, verbose_name='Αξία')
    day_added =  models.DateField(auto_now=timezone.now)
    payment_method = models.ForeignKey(PaymentMethod, null=True,verbose_name='Τρόπος Πληρωμής')

    class Meta:
        verbose_name="Αποδείξη Πληρωμής Πάγια"

    def __str__(self):
        return self.title   
    





