import random
import datetime
from faker import Faker


def get_past_date(generator, start_date, end_date=datetime.date.today()):
    return generator.date_between(start_date=start_date, end_date=end_date)


generator = Faker('en_US')

num_customers = random.randint(400, 1000)
num_transaction = num_customers * random.randint(0, 40)

with open('transaction_records.tsv', 'w') as transaction_file:
    transaction_file.write('ID\tUser_ID\tTransaction_Date\tTransaction_Quantity\tTransaction_Value\tProduct_Measure\tProduct_Size\tBrand\tCategory\tChain\n')
    transaction_id = 0
    measures = ['Box(s)', 'Unit(s)']
    brands = ['Vinda', 'Airwaves', 'Nike', 'Whatever']
    categories = ['groceries', 'shoes', 'snacks', 'beverage']
    countries = ['China', 'Japan', 'Hong Kong', 'Korea']

    with open('customer_records.tsv', 'w') as customer_file:
        customer_file.write('ID\tContact_Number\tContact_Email\tLast_Name\tFirst_Name\tDisplay_Name\tAge\tGender\tAddress\tCreate_Date\tLast_Modified_Date\tCountry\n')
        for i in range(1, num_customers+1):
            gender = 'Male' if random.randint(0,2) == 0 else 'Female'
            create_date = get_past_date(generator, start_date=datetime.date.today()-datetime.timedelta(days=730))
            modified_date = get_past_date(generator, start_date=create_date)

            customer_file.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\n'.format
                (
                    i,
                    generator.phone_number(),
                    generator.email(),
                    generator.last_name_male() if gender == 'Male' else generator.last_name_female(),
                    generator.first_name_male() if gender == 'Male' else generator.first_name_female(),
                    generator.user_name(),
                    random.randint(14, 75),
                    gender,
                    generator.address().replace('\n', ', '),
                    create_date,
                    modified_date,
                    countries[random.randint(0, len(countries)-1)]
                )
            )

            for j in range(random.randint(0, 40)):
                transaction_id += 1
                quantity = random.randint(1, 20)

                transaction_file.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\n'.format
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
