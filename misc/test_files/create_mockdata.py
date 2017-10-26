import random
import datetime
from faker import Faker
from collections import defaultdict


def get_past_date(generator, start_date, end_date=datetime.date.today()):
    return generator.date_between(start_date=start_date, end_date=end_date)


generator = Faker('en_US')

num_customers = random.randint(1500, 2000)
max_num_transaction = random.randint(0, 50)
customer_transaction_mapping = defaultdict(list)
num_campaign = random.randint(20, 50)
conversion_responses = ['Pending', 'Converted', 'Not Converted']
with open('transaction_records.tsv', 'w') as transaction_file:
    transaction_file.write('Transaction_ID\tUser_ID\tTransaction_Date\tTransaction_Quantity\tTransaction_Value\tProduct_Measure\tProduct_Size\tBrand\tCategory\tChain\n')
    transaction_id = 0

    measures = ['Box(s)', 'Unit(s)']
    brands = ['Vinda', 'Airwaves', 'Nike', 'Whatever']
    categories = ['groceries', 'shoes', 'snacks', 'beverage']
    countries = ['China', 'Japan', 'Hong Kong', 'Korea']

    with open('customer_records.tsv', 'w') as customer_file:
        customer_file.write('User_ID\tContact_Number\tContact_Email\tLast_Name\tFirst_Name\tDisplay_Name\tAge\tGender\tAddress\tCreate_Date\tLast_Modified_Date\tCountry\n')
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
                    random.choice(countries)
                )
            )

            for j in range(random.randint(0, max_num_transaction)):
                transaction_id += 1
                quantity = random.randint(1, 20)
                customer_transaction_mapping[i].append(transaction_id)
                transaction_file.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\n'.format
                    (
                        transaction_id,
                        i,
                        get_past_date(generator, create_date),
                        quantity,
                        quantity * round(random.uniform(5, 40), 2),
                        random.choice(measures),
                        random.randint(40, 300),
                        random.choice(brands),
                        random.choice(categories),
                        generator.country()
                    )
                )

with open('campaign_records.tsv', 'w') as campaign_file, open('conversion_records.tsv', 'w') as conversion_file:
    campaign_file.write('Campaign_ID\tCampaign_Name\tStart_Date\tEnd_Date\tChannel_ID\tSpending\tClicks\tImpressions\n')
    campaign_id = 0
    
    conversion_file.write('Conversion_ID\tCampaign_ID\tUser_ID\tResponse\tTransaction_ID\n')
    conversion_id = 0

    for i in range(1, num_campaign + 1):
        gender = 'Male' if random.randint(0, 2) == 0 else 'Female'
        start_date = get_past_date(generator, start_date=datetime.date.today() - datetime.timedelta(days=730))
        end_date = get_past_date(generator, start_date=create_date)
        num_impressions = random.randint(500, 100000)

        campaign_file.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\n'.format
        (
            i,
            generator.catch_phrase(),
            start_date,
            end_date,
            random.randint(1, 5),
            random.randint(10, 1000) / 100.0 * num_impressions,
            int(random.randint(15, 85) / 100.0 * num_impressions),
            num_impressions
        ))

        for j in range(random.randint(0, num_customers)):
            conversion_id += 1
            customer_id = random.choice(customer_transaction_mapping.keys())
            transaction_id = random.choice(customer_transaction_mapping[customer_id])
            response = random.choice(conversion_responses)

            conversion_file.write('{0}\t{1}\t{2}\t{3}\t{4}\n'.format
            (
                conversion_id,
                i,
                customer_id,
                response,
                random.choice(customer_transaction_mapping[customer_id]) if response == 'Converted' else None
            ))

channels = {'Tencent Social Ads': 'DSP', 'Baidu Advertising': 'Keyword Ads', 'Google AdWords': 'Keyword Ads', 'DoubleClick': 'Ad Exchange', 'EDM': 'EDM'}
with open('channel_records.tsv', 'w') as channel_file:
    channel_file.write('Channel_ID\tChannel_Name\tCountry\tCategory\n')
    for index, channel in enumerate(channels.keys()):
        channel_file.write('{0}\t{1}\t{2}\t{3}\n'.format(index+1, channel, random.choice(countries), channels[channel]))