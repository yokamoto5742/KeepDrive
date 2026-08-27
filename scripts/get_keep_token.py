"""Google Keep用マスタートークンを取得するセットアップ補助スクリプト。

gkeepapiはアプリパスワードでログインできないため、ブラウザで取得した
oauth_tokenをgpsoauthでマスタートークンに交換する必要がある。
"""

import getpass
import sys

import gpsoauth

ANDROID_ID = '0123456789abcdef'

INSTRUCTIONS = """\
=== Google Keep マスタートークン取得 ===

1. ブラウザのシークレットウィンドウで下記URLを開く
   https://accounts.google.com/EmbeddedSetup
2. Googleアカウントでログインする（2段階認証も完了させる）
3. 「同意する」をクリックする
4. 開発者ツール（F12）→ Application → Cookies から
   oauth_token クッキーの値をコピーする（oauth2_4/... で始まる文字列）
"""


def main() -> int:
    print(INSTRUCTIONS)

    email = input('Googleアカウントのメールアドレス: ').strip()
    oauth_token = getpass.getpass('oauth_tokenの値（入力は表示されません）: ').strip()

    if not email or not oauth_token:
        print('メールアドレスとoauth_tokenの両方を入力してください')
        return 1

    response = gpsoauth.exchange_token(email, oauth_token, ANDROID_ID)
    master_token = response.get('Token')

    if not master_token:
        print(f'マスタートークンを取得できませんでした: {response}')
        return 1

    print('\n取得に成功しました。以下を .env に貼り付けてください:\n')
    print(f'KEEP_EMAIL={email}')
    print(f'KEEP_MASTER_TOKEN={master_token}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
