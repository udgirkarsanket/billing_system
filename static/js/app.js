var app = angular.module('sakshi', []);
app.config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});
app.controller('HomeController', ['$scope','$http', function ($scope,$http) {
    $http.get('/get_stock').then(function(data){
    if(data.data.ok){
        $scope.products = data.data.products
    }})
    $scope.customfilter = function(row){
    return row['stock']<10
    }
}]);
app.controller('ViewController', ['$scope','$http','$filter', function ($scope,$http,$filter) {
$http.get('/get_all_stock').then(function(data){
if(data.data.ok){
    $scope.product_list = data.data.product_list.sort()
    $scope.stock = data.data.stock
    $scope.selected_product = $scope.product_list[0]
    $scope.calculate_stock()
}
})
$scope.calculate_stock = function(){
    $scope.total = 0
    $filter('filter')($scope.stock, {
                    'product_name': $scope.selected_product
                }).map(function(x){
                if(x['entry_type']=='sell'){
                $scope.total=$scope.total-x['qty']}
                if(x['entry_type']=='purchase'){
                $scope.total=$scope.total+x['qty']}})
}
}]);
app.controller('PrintController', ['$scope','$http', function ($scope,$http) {
$http.get('/get_receipts').then(function(data){
if(data.data.ok){
$scope.receipts = data.data.receipts}})
$scope.remove = function(row){
$http.get('/delete_receipt/'+row.receipt_id).then(function(data){
if(data.data.ok){
alert('Receipt Deleted Successfully');
window.location('/open_print_receipt');
}
})
}
}]);
app.controller('AddReceiptController', ['$scope','$http','$filter', function ($scope,$http,$filter) {
$scope.item_list=[]
$scope.available_stock = '-'
$scope.check_stock = function(){
    $scope.available_stock = $filter('filter')($scope.product_list, function(item){return item['product_name']==$scope.temp['product']})[0]['stock']
}
$scope.product_list=JSON.parse(document.getElementById('product_list_raw').value)
$scope.master_product_list = angular.copy($scope.product_list)
$scope.receipt_details = {}
$scope.receipt_details['cost']=0
$scope.receipt_details['cgst']=0
$scope.receipt_details['sgst']=0
$scope.receipt_details['total_cost']=0
$scope.add=function(){
        if ($scope.receipt_details['entry_type']=='sell' && $scope.available_stock >= $scope.temp.qty){
        valid=confirm("Available stock is "+$scope.available_stock+ " Do you still want to sell this product?")
        }
        if($scope.receipt_details['entry_type']=='purchase' || valid){
        $scope.item_list.push($scope.temp)
        $scope.product_list=$filter('filter')($scope.product_list, function(item){return item['product_name']!=$scope.temp['product']})
        if($scope.receipt_details['entry_type']=='sell'){
            $scope.temp.discount=0
            }
        $scope.receipt_details['cost']=$scope.receipt_details['cost']+($scope.temp.qty*$scope.temp.rate*(1-($scope.temp.discount/100)))
        $scope.receipt_details['cgst']=$scope.receipt_details['cost']*9/100
        $scope.receipt_details['sgst']=$scope.receipt_details['cost']*9/100
        $scope.receipt_details['total_cost']=($scope.receipt_details['cost']+$scope.receipt_details['cgst']+$scope.receipt_details['sgst'])
        $scope.temp = {}
        $scope.available_stock = '-'
        }
}
$scope.remove = function(row){
    $scope.item_list = $filter('filter')($scope.item_list, function(item){return item['product']!=row['product']})
    $scope.product_list.push($filter('filter')($scope.master_product_list, function(item){return item['product_name']==row['product']})[0])
    if($scope.receipt_details['entry_type']=='sell'){
        row.discount=0
        }
    $scope.receipt_details['cost']=$scope.receipt_details['cost']-(row.qty*row.rate*(1-(row.discount/100)))
    $scope.receipt_details['cgst']=$scope.receipt_details['cost']*9/100
    $scope.receipt_details['sgst']=$scope.receipt_details['cost']*9/100
    $scope.receipt_details['total_cost']=($scope.receipt_details['cost']+$scope.receipt_details['cgst']+$scope.receipt_details['sgst'])
}
$scope.convert_to_word = function(num){
    var units = [
        'Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight',
        'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen',
        'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'
    ]
    var tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
    if(num>20){
    return tens[parseInt(num/10)]+' '+((num%10>0)?units[num%10]:'')
    }
    else if(num<20){
    return units[num]
    }
}
$scope.formatAmount = function(amt){
    amt = amt.toFixed(2)
    var temp = []
    if(amt>99999){
    var lakhs = parseInt(amt/100000)
    temp.push($scope.convert_to_word(lakhs)+' Lakh')
    amt = amt - lakhs*100000
    }
    if(amt>999){
    var thousands = parseInt(amt/1000)
    temp.push($scope.convert_to_word(thousands)+' Thousands')
    amt = amt - thousands*1000
    }
    if(amt>99){
    var hundreds = parseInt(amt/100)
    temp.push($scope.convert_to_word(hundreds)+' Hundreds')
    amt = amt - hundreds*100
    }
    if(amt>0){
    if(temp.length>0){
    temp.push('and')}
    var units = parseInt(amt)
    temp.push($scope.convert_to_word(units) + ' Rupees')
    amt = amt - units
    }
    if(amt<1){
    var paise = parseInt(amt*100)
    temp.push($scope.convert_to_word(paise)+' Paise')
    amt=0
    }
    if(amt==0){
    temp.push(' Only')
    }
    return temp.join(' ')
    }
$scope.submit=function(){
    if($scope.item_list.length>0
    && $scope.receipt_details['customer_name']
     && $scope.receipt_details['entry_type']
      && $scope.receipt_details['creation_date']){
      $scope.receipt_details['creation_date']=moment($scope.receipt_details['creation_date']).format('YYYY-MM-DD')
    $scope.PostData = {}
    $scope.PostData['item_list'] = $scope.item_list
    $scope.PostData['receipt_details'] = $scope.receipt_details
    $http.post("/add_receipt",$scope.PostData).then(function(data){
    if(data.data.ok){
    alert("Receipt Added");
    window.location='/'}
    else{
    alert("Something Went Wrong!!!")
    }
    })
}
    else{
    var tmp = "Please Enter "
    if($scope.item_list.length==0){
    tmp = tmp+'Atleast 1 Product, '
    }
    if(!$scope.receipt_details['customer_name']){
    tmp = tmp+'Enter Customer Name, '
    }
    if(!$scope.receipt_details['entry_type']){
    tmp = tmp+'Please select receipt type, '
    }
    if(!$scope.receipt_details['creation_date']){
    tmp = tmp+'Please select date for receipt.'
    }
    alert(tmp)
    }
}
$scope.addProduct = function(){
    $http.post('/add_product',$scope.new_product).then(function(data){
    if(data.data.ok){
        alert("product Added Successfully");
        $scope.new_product['stock'] = 0;
        $scope.new_product['product_name'] = data.data.product_name;
        $scope.product_list.push($scope.new_product);
        }
    else{
        alert("Somehing Went Wrong")}
    })
}
}]);
app.controller('AddProductController', ['$scope','$http', function ($scope,$http) {
$scope.new_product = {}
$http.get('/products_available').then(function(data){
    if(data.data.ok){
        $scope.products = data.data.product_list
    }
})
$scope.add = function(){
    $http.post('/add_product',$scope.new_product).then(function(data){
    if(data.data.ok){
        alert("product Added Successfully");
        window.location='/open_add_product'}
    else{
        alert("Somehing Went Wrong")}
    })
}
$scope.editProduct= function(row){
$scope.new_product = row
}
$scope.deleteProduct =function(row){
valid = confirm("Do you want to delete product: "+row['product_name'])
if(valid){
$http.get('/delete_product/'+row['product_id']).then(function(data){
    if(data.data.ok){
        alert("Product Deleted Successfully");
        window.location='/open_add_product'}
    else{
        alert("Somehing Went Wrong")}
    })
}
}
}]);