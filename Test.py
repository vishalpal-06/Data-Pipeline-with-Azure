import yaml

with open('Config.yaml', 'r') as configuration:
    config = yaml.load(configuration, Loader=yaml.SafeLoader)


print(config['Screener']['id'])
print(config['Screener']['pass'])
