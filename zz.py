import awspricing

ec2_offer = awspricing.offer('AmazonEC2', region='us-east-1')
# ec2_offer = awspricing.offer('AmazonEC2')

a = ec2_offer.search_skus(
  instance_type='c4.2xlarge',
  location='US East (N. Virginia)',
  operating_system='Linux',
  capacity_status='Used'
)

print(a)
# b = ec2_offer.reserved_hourly(
#   'c4.large',
#   operating_system='Linux',
#   lease_contract_length='3yr',
#   purchase_option='Partial Upfront',
#   region='us-east-1'
# )

# b = ec2_offer.ondemand_hourly('c4.2xlarge', region='us-east-1', operating_system='Linux', )

# print(b)
