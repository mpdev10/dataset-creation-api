from dataset_creation_api.DatasetCreator import DatasetCreator

if __name__ == '__main__':
    creator = DatasetCreator(root_dir='Categories',
                             urls={'https://atlas-roslin.pl/dziko-rosnace-owoce-jadalne.htm',
                                   'https://atlas-roslin.pl/rosliny-trujace.htm'},
                             classes={'name-latin'})

    creator.create_directories()
    creator.scrape_data(max_request_num=1,
                        keywords='fruit')
