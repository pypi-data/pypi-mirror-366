class Version:
    _instances = {}  # class-level cache for singleton instances

    @staticmethod
    def version_factory(version_of_data):
        from customer_purchases.v1 import V1_version  # Lazy import
        # from customer_purchases.v2 import V2_version  # Uncomment when V2 is implemented
        if version_of_data not in Version._instances:
            if version_of_data == 'v1':
                Version._instances[version_of_data] = V1_version()
            # elif version_of_data == 'v2':
            #     Version._instances[version_of_data] = V2_version()
            else:
                raise Exception('Unknown version.')
        return Version._instances[version_of_data]

    def create_data_type(self, type_of_data):
        raise Exception('This method must be implemented or rewritten.')
