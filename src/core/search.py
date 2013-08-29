# -*- coding: utf-8 -*-

import xbmcup.gui

from common import RenderArtists, COVER_NOALBUM
from api import lastfm, vk

class SearchLastFM(xbmcup.app.Handler, RenderArtists):
    def handle(self):
        sources = [('artist', u'Исполнители'), ('album', u'Альбомы'), ('track', u'Композиции'), ('tag', u'Теги')]
        source = xbmcup.gui.select(u'Что ищем?', sources)
        if source is None:
            self.render()
        else:
            query = xbmcup.gui.prompt([x[1] for x in sources if x[0] == source][0])
            if not query:
                self.render()
            else:
                if source == 'artist':
                    self.search_artist(query)
                elif source == 'album':
                    self.search_album(query)
                elif source == 'track':
                    self.search_track(query)
                else:
                    self.search_tag(query)


    def search_artist(self, query):
        self.render_artists(lastfm.artist.search(artist=query, limit=200))
        self.render(content='artists', mode='thumb')


    def search_album(self, query):
        for album in lastfm.album.search(query, limit=200):

            title = album['name']
            if album['artist']:
                title = u'[B]' + album['artist'] + '[/B]  -  ' + title

            item = dict(
                url    = self.link('tracks', mbid=album['mbid'], name=album['name'], artist=album['artist'], tags=[], fromalbum=1),
                title  = title,
                folder = True,
                menu   = [],
                menu_replace = True
            )

            if album['artist']:
                item['menu'].append((u'Добавить альбом в плейлист', self.link('playlist-add-album', mbid=album['mbid'], name=album['name'], artist=album['artist'])))

            item['menu'].append((u'Настройки дополнения', self.link('setting')))

            if album['image']:
                item['cover'] = album['image']
                item['fanart'] = album['image']
            else:
                item['cover'] = COVER_NOALBUM

            self.item(**item)

        self.render(content='albums', mode='list')


    def search_track(self, query):
        for i, track in enumerate(lastfm.track.search(track=query, limit=200)):

            item = dict(
                url    = self.resolve('play-audio', artist=track['artist'], song=track['name']),
                title  = u'[B]' + track['artist'] + '[/B]  -  ' + track['name'],
                media  = 'audio',
                info   = {'title': track['name']},
                menu   = [(u'Информация', self.link('info')), (u'Добавить трэк в плейлист', self.link('playlist-add', artist=track['artist'], song=track['name'])), (u'Настройки дополнения', self.link('setting'))],
                menu_replace = True
            )

            item['info']['artist'] = track['artist']
            
            item['info']['tracknumber'] = i + 1

            if track['image']:
                item['cover'] = track['image']
                item['fanart'] = track['image']
            else:
                item['cover'] = COVER_NOALBUM

            self.item(**item)

        self.render(content='songs', mode='list')


    def search_tag(self, query):
        tags = lastfm.tag.search(tag=query, limit=200)

        for tag in tags:
            self.item(tag['name'].capitalize(), self.link('tags', tag=tag['name']), folder=True, cover=self.parent.cover)

        self.render(mode='list')



class SearchVK(xbmcup.app.Handler):
    def handle(self):
        query = xbmcup.gui.prompt(u'Поиск ВКонтакте')
        if query:
            result = vk.api('audio.search', q=query, auto_complete=1, count=300)
            if result:
                total = len(result['items'])

                for i, r in enumerate(result['items']):

                    item = dict(
                        url    = self.resolve('play-audio', url=r['url'], artist=r['artist'], title=r['title'], duration=r['duration']),
                        title  = u'[B]' + r['artist'] + u'[/B] - ' + r['title'],
                        media  = 'audio',
                        info   = {'title': r['title']},
                        menu   = [(u'Информация', self.link('info')), (u'Настройки дополнения', self.link('setting'))],
                        menu_replace = True,
                        total  = total
                    )

                    item['info']['artist'] = r['artist']
                    item['info']['duration'] = r['duration']
                    
                    item['info']['tracknumber'] = i + 1

                    self.item(**item)

        self.render(content='songs', mode='list')