import unicodedata
location_mapper = {
    "An Giang": "geoId-AGG",
    "Ba Ria - Vung Tau": "geoId-BR-VT",
    "BRVT": "geoId-BR-VT",
    "Binh Duong": "geoId-BDG",
    "Binh Phuoc": "geoId-BPC",
    "Binh Thuan": "geoId-BTN",
    "Binh Dinh": "geoId-BDH",
    "Bac Lieu": "geoId-BLU",
    "Bac Giang": "geoId-BGG",
    "Bac Kan": "geoId-BKN",
    "Bac Ninh": "geoId-BNH",
    "Ben Tre": "geoId-BTE",
    "Cao Bang": "geoId-CBG",
    "Viet Nam": "geoId-VNM",
    "Can Tho": "geoId-CTO",
    "Ca Mau": "geoId-CMU",
    "Gia Lai": "geoId-GLI",
    "Kon Tum": "geoId-KTM",
    "Hoa Binh": "geoId-HBH",
    "Ha Giang": "geoId-HGG",
    "Ha Nam": "geoId-HNM",
    "Ha Noi": "geoId-HNI",
    "Ha Tinh": "geoId-HTH",
    "Ha Tay": "geoId-HNI",
    "Hung Yen": "geoId-HYN",
    "Hai Duong": "geoId-HDG",
    "Hai Phong": "geoId-HPG",
    "Hau Giang": "geoId-HGG",
    "Khanh Hoa": "geoId-KHA",
    "Kien Giang": "geoId-KGG",
    "Lai Chau": "geoId-LCU",
    "Long An": "geoId-LAN",
    "Lao Cai": "geoId-LCI",
    "Lam Dong": "geoId-LDG",
    "Lang Son": "geoId-LSN",
    "Nam Dinh": "geoId-NDH",
    "Nghe An": "geoId-NAN",
    "Ninh Binh": "geoId-NBH",
    "Ninh Thuan": "geoId-NTN",
    "Phu Tho": "geoId-PTO",
    "Phu Yen": "geoId-PYN",
    "Quang Binh": "geoId-QBH",
    "Quang Nam": "geoId-QNM",
    "Quang Ngai": "geoId-QNI",
    "Quang Ninh": "geoId-QNH",
    "Quang Tri": "geoId-QTI",
    "Soc Trang": "geoId-STG",
    "Son La": "geoId-SLA",
    "Thanh Hoa": "geoId-THA",
    "Thai Binh": "geoId-TBH",
    "Thai Nguyen": "geoId-TNN",
    "Thua Thien Hue": "geoId-TTH",
    "Thua Thien - Hue": "geoId-TTH",
    "TT-Huế": "geoId-TTH",
    "Tien Giang": "geoId-TGG",
    "TP.Ho Chi Minh": "geoId-HCM",
    "TP. Ho Chi Minh": "geoId-HCM",
    "TP.HCM": "geoId-HCM",
    "Trung du va mien nui phia Bac": "geoId-NT",
    "Tra Vinh": "geoId-TVH",
    "Tuyen Quang": "geoId-TQG",
    "Tay Nguyen": "geoId-TNN",
    "Tay Ninh": "geoId-TNH",
    "Vinh Long": "geoId-VLG",
    "Vinh Phuc": "geoId-VPC",
    "Yen Bai": "geoId-YBI",
    "Dien Bien": "geoId-DBN",
    "Da Nang": "geoId-DNG",
    "Dong Nam Bo": "geoId-ST",
    "Dak Lak": "geoId-DLK",
    "Dak Nong": "geoId-DNG1",
    "Dong bang song Cuu Long": "geoId-MRD",
    "Dong bang song Hong": "geoId-RRD",
    "Dong Nai": "geoId-DNI",
    "Dong Thap": "geoId-DTP",
    "Bac Trung Bo và duyen hai mien Trung": "geoId-SCC",
    "Bac Trung Bo va Duyen hai mien Trung": "geoId-SCC",
    "Ca Nuoc": "geoId-VNM"
}
def normalize_location(location):
    if not isinstance(location, str):
        return location
    # Chuẩn hóa Unicode về dạng NFC 
    location = unicodedata.normalize('NFC', location)
    # Chuẩn hóa Unicode về dạng không dấu
    location = ''.join(
        c for c in unicodedata.normalize('NFD', location) if unicodedata.category(c) != 'Mn'
    )
    # Thay thế chữ Đ và đ
    location = location.replace('Đ', 'D').replace('đ', 'd')
    return location.lower()

normalized_location_mapper = {normalize_location(k): v for k, v in location_mapper.items()}

print(normalize_location('Bình Định') == normalize_location('Binh Dinh'))
stat_var_group_mapper = {
    'Demographics': 2,
    'Education': 3,
    'Economy': 4,
    'Health': 5,
    'Housing': 6,
    'Environment': 7,
    'Energy': 8,
    'Social security': 9,
    'Agriculture, Forestry and fishery': 10,
    'Administrative unit and Land': 11,
    'Culture': 12,
    'Sports': 13,
    'Population': 14,
    'Employment': 15,
    'National Accounts': 16,
    'Banking, Insurance, and Budget Revenues and Expenditures': 17,
    'Investment and Construction': 18,
    'Industry': 19,
    'Enterprise': 20,
    'Trade and Services': 21,
    'Price Statistics': 22,
    'Living Standards': 23,
    'Science and technology': 24,
}


def provenance_id_mapper(tab_name, index):
    if tab_name == 'Dân số':
        return stat_var_group_mapper['Population']
    elif tab_name == 'Lao động việc làm':
        return stat_var_group_mapper['Employment']
    elif tab_name == 'Tài khoản quốc gia':
        return stat_var_group_mapper['National Accounts']
    if tab_name == 'Ngân hàng, bảo hiểm và thu chi ngân sách':
        return stat_var_group_mapper['Banking, Insurance, and Budget Revenues and Expenditures']
    elif tab_name == 'Nông, Lâm nghiệp và Thủy sản':
        return stat_var_group_mapper['Agriculture, Forestry and fishery']
    elif tab_name == 'Đầu tư và Xây dựng':
        return stat_var_group_mapper['Investment and Construction']
    if tab_name == 'Công nghiệp':
        return stat_var_group_mapper['Industry']
    elif tab_name == 'Doanh nghiệp':
        return stat_var_group_mapper['Enterprise']
    elif tab_name == 'Thương mại và Dịch vụ':
        return stat_var_group_mapper['Trade and Services']
    if tab_name == 'Thống kê Giá':
        return stat_var_group_mapper['Price Statistics']
    elif tab_name == 'Giáo dục':
        return stat_var_group_mapper['Education']
    elif tab_name == 'Y tế, mức sống dân cư, văn hóa, thể thao, trật tự an toàn xã hội và môi trường':
        if(0 <= index and index <= 20):
            return stat_var_group_mapper['Health']
        elif (index in ['21','22','23','25']):
            return stat_var_group_mapper['Culture']
        elif (index == 24):
            return stat_var_group_mapper['Sports']
        elif(26 <=index and index <= 68):
            return stat_var_group_mapper["Living Standards"]
        elif(69 <= index and index <=91):
            return stat_var_group_mapper['Social security']
        elif(93 <= index and index <= 95):
            return stat_var_group_mapper['Science and technology']
        else:
            return stat_var_group_mapper['Environment']
    if tab_name == 'Đơn vị hành chính, Đất đai và Khí hậu':
        if (index <= 4) :
            return stat_var_group_mapper['Administrative unit and Land']  
        else: 
            return stat_var_group_mapper['Environment']
    else:
        return 1  # Giá trị mặc định
