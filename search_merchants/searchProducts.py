from builtins import list, len
from .distanceCoordinates import distanceInKMBetweenCoordinates
from search_merchants.searchMerchant import getAllMerchants

def sortByDistance(cur,data_res,merchantid,radius):
    finalResult = []

    cur.execute("select Latitude,Longitude FROM Location WHERE MerchantID = " + str(merchantid))
    a = cur.fetchall()
    currentLatitude = float(a[0]["Latitude"])
    currentLongitude = float(a[0]["Longitude"])
    cur.close()

    for i in range(len(data_res)):
        latitude = float(data_res[i]["Latitude"])
        longitude = float(data_res[i]["Longitude"])
        distance = distanceInKMBetweenCoordinates(currentLatitude, currentLongitude, latitude, longitude)
        dic = {"distance": distance}
        dic.update(data_res[i])
        if not radius:
            finalResult.append(dic)
        else:
            if (distance <= float(radius)):
                finalResult.append(dic)

    finalResult = sorted(finalResult, key=lambda i: i['distance'])
    print(finalResult)
    return finalResult

def getSearchResults(mysql,merchantid,name='',search_option='initial',filters=False,radius=2000):
    cur = mysql.connection.cursor()
    if search_option=='initial':
        data_res= getAllMerchants(mysql,merchantid,radius)
    elif search_option=='product':
        product=name
        # only offers filter
        # add exact matches then based on name then see similarity in name
        cur.execute("SELECT * from Location,Merchant,Product WHERE (Product.Name like %s OR Category like %s ) and Product.MerchantID <> %s and Product.MerchantID=Merchant.MerchantID and Location.MerchantID=Merchant.MerchantID",
                ("%"+product+"%","%"+product+"%",merchantid))
        data = list(cur.fetchall())

        # similar category search
        product_tags=product.split(" ")
        if len(product_tags)>1:
            for i in product_tags:
                cur.execute("SELECT * from Location,Merchant,Product WHERE Category LIKE %s and Product.MerchantID <> %s and Location.MerchantID=Merchant.MerchantID", ( i,merchantid))
                x=list(cur.fetchall())
                data.extend(x)

        # make search unique and append discount info only valid ones
        res=[]
        data_res=[]
        for i in range(len(data)):
            if data[i]['ProductID'] not in res:
                cur.execute("select distinct * from Product,Offer,OfferOnProduct where OfferOnProduct.ProductID=%s and Product.ProductID = OfferOnProduct.ProductID and  OfferOnProduct.offerID = Offer.offerID and CURDATE()<=ValidTill ", (data[i]['ProductID'],))
                x=list(cur.fetchall())
                if filters and not x:
                    pass
                else:
                    data[i]['Offers']=x
                    res.append(data[i]['ProductID'])
                    data_res.append(data[i])
        
    else:
        merchant=name
        if filters:
            cur.execute("SELECT distinct LocationID, Latitude, Longitude ,Merchant.MerchantID,Merchant.Name from Location,Merchant,Product,Offer,OfferOnProduct WHERE Merchant.Name LIKE %s and Merchant.MerchantID <> %s and Product.MerchantID=Merchant.MerchantID and Product.ProductID = OfferOnProduct.ProductID and OfferOnProduct.offerID = Offer.offerID and CURDATE()<=ValidTill and Location.MerchantID=Merchant.MerchantID", ("%"+merchant+"%", merchantid))
            data = list(cur.fetchall())
        else:
            # add exact matches then based on name then see similarity in name
            cur.execute("SELECT * from Location,Merchant WHERE Merchant.Name like %s and Merchant.MerchantID <> %s  and Location.MerchantID=Merchant.MerchantID",("%"+merchant+"%",merchantid))
            data = list(cur.fetchall())
        data_res = []
        for i in data:
            cur.execute("select distinct * from Product,Offer,OfferOnProduct where Product.MerchantID=%s and Product.ProductID = OfferOnProduct.ProductID and OfferOnProduct.offerID = Offer.offerID and CURDATE()<=ValidTill", (i['MerchantID'],))
            x = list(cur.fetchall())
            i['Offers'] = x
            data_res.append(i)
    
    finalResult=sortByDistance(cur,data_res,merchantid,radius)
    return finalResult