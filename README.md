# 学生向けSNSアプリ
開発期間**2020年10月1日~12月26日**

**使用フレームワーク**: **Django** 

更新日**2021年2月20日**

編集者**yut7G8**

**[HAIT_Lab_Advancedコース](https://hait-lab.com/)2期 Eチームメンバー**

yut7G8, amazing-tomotoshi, ham-sh, Kkzs30842107

## 開発背景

1. **サークル目線**

新歓やイベントの参加学生の管理を簡単にしたい

2. **学生目線**

新歓期にサークルの情報を閲覧したい

企業の情報を知り、就活に役立てたい

3. **企業目線**

学生に向けたピンポイントな情報を流したい

## 使い方
1. **DBの作成**
```
python manage.py makemigrations app
python manage.py migrate
```
2. **起動**(ローカルパス指定)
```
python manage.py runserver
```

## 各種担当機能(参考サイト)

機能ごとに役割分担をしたため、各々が機能ごとのフロントエンド/バックエンドを担当しています。

### ham-sh
1. [アカウント新規作成・ログイン機能](https://blog.narito.ninja/detail/38/)

2. [フォロー機能](https://jyouj.hatenablog.com/entry/2018/06/04/000311)

3. イベント投稿(新規作成・編集削除)

4. [セキュリティ(学生・サークル)](https://stackoverrun.com/ja/q/12115655)

### yut7G8
1. [投稿機能(新規作成・編集・削除)](https://note.com/takuya814/m/m829ed8312291)

2. [いいねボタン](https://note.com/takuya814/n/n896441e790ba?magazine_key=m829ed8312291)

3. GitHubの管理

### kkzs30842107
1. [検索機能](https://note.com/takuya814/n/ndde42e157fe0?magazine_key=m829ed8312291)

2. URL追加機能

3. 企業アカウント作成

### amazing-tomotoshi
1. [ユーザー情報(表示・編集)](https://blog.narito.ninja/detail/43/)

2. [アイコン表示](https://blog.ver001.com/css-image-border-radius-object-fit/)

3. [タブ機能](https://ics.media/entry/190826/)

4. [デザイン修正(HTML, CSS)](https://qiita.com/nakanishi03/items/c80a16b9b9796c25f890)

#### 注意
**無断転載禁止**
