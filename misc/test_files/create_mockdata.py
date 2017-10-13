import random
import datetime
from faker import Faker


def get_past_date(generator, start_date, end_date=datetime.date.today()):
    return generator.date_between(start_date=start_date, end_date=end_date)


generator = Faker('en_US')

num_customers = random.randint(400, 1000)
num_transaction = num_customers * random.randint(0, 40)

with open('transaction_records.csv', 'w') as transaction_file:
    transaction_file.write('ID,User_ID,Transaction_Date,Transaction_Value,Product_Measure,Product_Size,Brand,Category,Chain\n')
    transaction_id = 0
    measures = ['Box(s)', 'Unit(s)']
    brands = ['Vinda', 'Airwaves', 'Nike', 'Whatever']
    categories = ['groceries', 'shoes', 'snacks', 'beverage']

    with open('customer_records.csv', 'w') as customer_file:
        customer_file.write('ID,Contact_Number,Contact_Email,Last_Name,First_Name,Display_Name,Age,Gender,Address,Create_Date,Last_Modified_Date,Country\n')
        for i in range(1, num_customers+1):
            gender = 'Male' if random.randint(0,2) == 0 else 'Female'
            create_date = get_past_date(generator, start_date=datetime.date.today()-datetime.timedelta(days=730))
            modified_date = get_past_date(generator, start_date=create_date)

            customer_file.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}\n'.format
                (
                    i,
                    generator.phone_number(),
                    generator.email(),
                    generator.last_name_male() if gender == 'Male' else generator.last_name_female(),
                    generator.first_name_male() if gender == 'Male' else generator.first_name_female(),
                    generator.user_name(),
                    random.randint(14, 75),
                    generator.address().replace('\n', ', '),
                    create_date,
                    modified_date,
                    generator.country()
                )
            )

            for j in range(random.randint(0, 40)):
                transaction_id += 1
                quantity = random.randint(1, 20)

                transaction_file.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n'.format
                    (
                        transaction_id,
                        i,
                        get_past_date(generator, create_date),
                        quantity,
                        quantity * round(random.uniform(5, 40), 2),
                        measures[random.randint(0, len(measures)-1)],
                        random.randint(40, 300),
                        brands[random.randint(0, len(brands)-1)],
                        categories[random.randint(0, len(categories)-1)],
                        generator.country()
                    )
                )
