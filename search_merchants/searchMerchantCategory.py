def getMerchantCategoryCode(mysql,category):
    category = category.upper()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM MerchantCategoryCode WHERE Category LIKE '{}'".format("%" + category + "%"))
    data = list(cur.fetchall())
    return data