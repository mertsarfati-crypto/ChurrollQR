var appname = angular.module('myqr', []);
appname.controller('master', ['$scope' ,'$timeout',
    function ($scope, $timeout) {
        /*
            Language Popup
        */

        $scope.basketItems = [];
        $scope.isBasket = false;
        $scope.isLanguagePopup = false;
        $scope.openCloseLanguagePopup = function () {
            $scope.isLanguagePopup = !$scope.isLanguagePopup;
        }

        $scope.openCloseBasket = function () {
            $scope.isBasket = !$scope.isBasket;
        }

        /*
            Theme Mode
        */

        $scope.theme = "light";
        $scope.changeThemeMode = function (mode) {
            if (mode === "light") {
                localStorage.setItem("myqrThemeMode", "light");
                $scope.theme = "light";
            } else {
                localStorage.setItem("myqrThemeMode", "dark");
                $scope.theme = "dark";
            }
        }


        $scope.isSearch = true;
        $scope.isPopupHide = false;
        $scope.init = function (mode, searchInputs) {
            $scope.isSearch = searchInputs;
            var modeFromLocalStorage = localStorage.getItem("myqrThemeMode");
            if (modeFromLocalStorage)
                $scope.theme = modeFromLocalStorage;
            else {
                if (mode === 'auto') {
                    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)
                        $scope.theme = "dark";
                } else if (mode === 'dark')
                    $scope.theme = "dark";
            }

            var basketItemsFromLocalStorage = localStorage.getItem("myqrBasketItems");
            if (basketItemsFromLocalStorage)
                $scope.basketItems = JSON.parse(basketItemsFromLocalStorage);

            var popupClosedDate = localStorage.getItem("myQrPopupClosed");
            if (popupClosedDate) {
                var nowDate = new Date();
                var condition = new Date(nowDate - Date.parse(popupClosedDate)).getMinutes();
                if (condition > 20) {
                    localStorage.removeItem("myQrPopupClosed");
                    $scope.isPopupHide = false;
                } else
                    $scope.isPopupHide = true;
            } else {
                $scope.isPopupHide = false;
            }
        }


        $scope.isMenu = false;

        $scope.openCloseMenu = function () {
            $scope.isMenu = !$scope.isMenu;
        }

        $scope.isFilter = false;

        $scope.openCloseFilterPopup = function () {
            $scope.isFilter = !$scope.isFilter;
        }

        $scope.addBasketSuccessShow = false;

        $scope.addBasket = function (data) {
            $scope.addBasketSuccessShow = true;
            $timeout(function () { 
                $scope.addBasketSuccessShow = false;
            }, 2000); 
            const item = $scope.basketItems.findIndex(i => i.id === data.id);
            if (item === -1) {
                data.quantity = 1;
                $scope.basketItems.push(data);
            } else
                $scope.basketItems[item].quantity = $scope.basketItems[item].quantity + 1;
            localStorage.setItem('myqrBasketItems', JSON.stringify($scope.basketItems));
        }

        $scope.addBasketFromPopup = function (data, isCurrencyLeft, link) {
            $scope.addBasket({
                id: data.ProductId,
                link: link,
                productTitle: data.ProductName,
                isCurrencyLeft: isCurrencyLeft ? true : false,
                variation: '',
                price: data.ProductPriceWithDiscount ?? data.ProductPrice ?? '',
                picture: data.ProductPicture,
                currency: data.PriceExchange
            });
        }

        $scope.addVariationToBasketFromPopup = function (data, variation, isCurrencyLeft, link) {
            $scope.addBasket({
                id: data.ProductId,
                link: link,
                productTitle: data.ProductName,
                isCurrencyLeft: isCurrencyLeft ? true : false,
                variation: variation.PriceTitle,
                price: variation.Price,
                picture: data.ProductPicture,
                currency: data.PriceExchange
            });
        }

        $scope.removeBasketItem = function (id) {
            const item = $scope.basketItems.findIndex(i => i.id === id);
            if (item === -1) return;
            $scope.basketItems.splice(item, 1);

            localStorage.setItem('myqrBasketItems', JSON.stringify($scope.basketItems));
        }

        $scope.clearBasket = function () {
            $scope.basketItems = [];
            localStorage.removeItem('myqrBasketItems');
        }

        $scope.isClosedMenuClose = false;
        $scope.openCloseClosedMenu = function () {
            $scope.isClosedMenuClose = true;
        }

        $scope.closePopup = function () {
            $scope.isPopupHide = true;
            localStorage.setItem("myQrPopupClosed", new Date());
        }

    }
]);
appname.controller('categoryDetail', ['$scope',
    function ($scope) {

        $scope.isPriceList = false;
        $scope.priceList = [];
        $scope.currencyIsLeft = 'left';
        $scope.currency = '';
        $scope.productTitle = '';

        $scope.setPrices = function (data, currencyPos, currencyStr, productTitle) {
            $scope.priceList = JSON.parse(data);
            $scope.isPriceList = true;
            $scope.currencyIsLeft = currencyPos;
            $scope.currency = currencyStr;
            $scope.productTitle = productTitle;
        }

        $scope.closePriceList = function () {
            $scope.isPriceList = false;
        }


        $scope.isProductDetail = false;
        $scope.productDetail = null;
        $scope.productDetailLink = "";
        $scope.productCurrencyIsLeft = "left";

        $scope.closeProductDetailPopup = function () {
            $scope.isProductDetail = false;
            $scope.productDetail = null;
            $scope.productDetailLink = "";
            $scope.productCurrencyIsLeft = "left";
        }

        $scope.openProductDetailPopup = function (data, link, currencyPos) {
            try{   
                $scope.productDetail = JSON.parse(data);
                $scope.isProductDetail = true;
                $scope.productDetailLink = link;
                $scope.productCurrencyIsLeft = currencyPos;

            } catch (err){  
                window.location.href=link;
            }
           
        }

    }
]);