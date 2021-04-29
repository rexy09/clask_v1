from django import forms
from .models import *
from django.db.models import F


class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = "__all__"
        exclude = ["business"]


class InventoryForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop("business")
        super(InventoryForm, self).__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(business=self.business)
        self.fields['product'].empty_label = "Select Product"
     
    class Meta:
        model = Inventory
        fields = "__all__"
        exclude = ["business", "remain", "damage","exist"]


class InventoryUpdateForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop("business")
        super(InventoryUpdateForm, self).__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(business=self.business)
        self.fields['product'].empty_label = "Select Product"
     
    class Meta:
        model = Inventory
        fields = "__all__"
        exclude = ["business","exist"]        


class CustomerForm(forms.ModelForm):
    
    class Meta:
        model = Customer
        fields = "__all__"
        exclude = ["business","category","points"]


class SaleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop("business")
        super(SaleForm, self).__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.filter(business=self.business,)
        self.fields['customer'].empty_label = "Select Customer"
        self.inventory_qs = Inventory.objects.filter(business=self.business).annotate(available=F('remain')-F('damage'))
        self.fields['inventory'].queryset = self.inventory_qs.filter(available__gt=0).order_by('-pk')
        self.fields['inventory'].empty_label = "Select Product"
    
    class Meta:
        model = Sale
        fields = "__all__"
        exclude = ["branch","user"]



class ExpenseForm(forms.ModelForm):    

    class Meta:
        model = Expense
        fields = '__all__'
        exclude = ['business']
        


class PayrollForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop("business")
        super(PayrollForm, self).__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(business=self.business)
        self.fields['employee'].empty_label = "Select Employee"    

    class Meta:
        model = Payroll
        fields = '__all__'
        exclude = ['business', 'tax_amount', 'paye_amount', 'sdl_amount', 'loan_debt']



class TakehomeForm(forms.ModelForm):

    class Meta:
        model = Takehome
        fields = '__all__'
        exclude = ['business']



class FixedAssetForm(forms.ModelForm):
    
    class Meta:
        model = FixedAsset
        fields = '__all__'
        exclude = ['business']



class SupplierForm(forms.ModelForm):
    
    class Meta:
        model = Supplier
        fields = '__all__'
        exclude = ['business']


class PurchaseOrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop("business")
        super(PurchaseOrderForm, self).__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.filter(business=self.business,)
        self.fields['supplier'].empty_label = "Select Supplier"
        self.fields['delivery'].queryset = Branch.objects.filter(business=self.business,)
        self.fields['delivery'].empty_label = "Select Branch"
    
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        exclude = ['business','employee','authorized']


class PurchaseOrderListForm(forms.ModelForm):
    
    class Meta:
        model = PurchaseOrderList
        fields = '__all__'
        exclude = ['purchase_order',]


PurchaseOrderListFormSet = forms.inlineformset_factory(PurchaseOrder, PurchaseOrderList,form=PurchaseOrderListForm, extra=3)
PurchaseOrderListUpdateFormSet = forms.inlineformset_factory(PurchaseOrder, PurchaseOrderList,form=PurchaseOrderListForm, extra=0)



class LocalPurchaseOrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop("business")
        super(LocalPurchaseOrderForm, self).__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.filter(business=self.business,)
        self.fields['supplier'].empty_label = "Select Supplier"
        self.fields['delivery'].queryset = Branch.objects.filter(business=self.business,)
        self.fields['delivery'].empty_label = "Select Branch"
    
    class Meta:
        model = LocalPurchaseOrder
        fields = '__all__'
        exclude = ['business','employee','authorized']


class LocalPurchaseOrderListForm(forms.ModelForm):
    
    class Meta:
        model = LocalPurchaseOrderList
        fields = '__all__'
        exclude = ['purchase_order',]


LocalPurchaseOrderListFormSet = forms.inlineformset_factory(LocalPurchaseOrder, LocalPurchaseOrderList,form=LocalPurchaseOrderListForm, extra=3)
LocalPurchaseOrderListUpdateFormSet = forms.inlineformset_factory(LocalPurchaseOrder, LocalPurchaseOrderList,form=LocalPurchaseOrderListForm, extra=0)   



class AccountsFixedAssetForm(forms.ModelForm):
    
    class Meta:
        model = AccountsFixedAsset
        fields = '__all__'  
        exclude = ['business']



class AccountsCurrentAssetForm(forms.ModelForm):
    
    class Meta:
        model = AccountsCurrentAsset
        fields = '__all__'    
        exclude = ['business']

        

class LiabilityForm(forms.ModelForm):
    
    class Meta:
        model = Liability
        fields = '__all__'    
        exclude = ['business']



class CheckAccountForm(forms.ModelForm):
    
    class Meta:
        model = CheckAccount
        fields = '__all__'
        exclude = ['remaining', 'business', 'employee', 'debit' ,'credit', 'description']   


class SavingAccountForm(forms.ModelForm):
    
    class Meta:
        model = SavingAccount
        fields = '__all__'
        exclude = ['remaining', 'business', 'employee', 'debit','credit', 'description']   

         
class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = '__all__'
        exclude = ['business']


class TaxForm(forms.ModelForm):
    
    class Meta:
        model = Tax
        fields = '__all__'
        exclude = ['business',"remain"]


class InterestForm(forms.ModelForm):

    class Meta:
        model = Interest
        fields = '__all__'
        exclude = ['business', 'debt', 'repayment', 'remaining']


class LoanForm(forms.ModelForm):

    class Meta:
        model = Loan
        fields = '__all__'
        exclude = ['business', 'remaining_debt', 'debt']


class PaymentForm(forms.Form):    
    payment = forms.DecimalField(max_digits=19, decimal_places=2)



