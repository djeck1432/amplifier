import argparse
import inst,vkontakte,fb

parser = argparse.ArgumentParser(
    description='instagram - Статистика из Instagram  за 3 месяца. ' \
                'facebook - В статистике из Facebook есть все комментаторы и все реакции на посты за последний месяц' \
                'vkontakte - В статистике из ВКонтакте только комментаторы, которые лайкали посты.'
)
parser.add_argument('social_network',help='Статистика по : instagram,facebook,vkontakte')
args = parser.parse_args()

if __name__=='__main__':
    if args.social_network == 'instagram':
        inst.main()
    elif args.social_network == 'facebook':
        fb.main()
    elif args.social_network == 'vkontakte':
        vkontakte.main()