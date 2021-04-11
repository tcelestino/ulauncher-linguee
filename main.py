import urllib.request, urllib.parse, urllib.error
import logging
import requests

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction

LOGGER = logging.getLogger(__name__)

def urlencode(q):
    return urllib.parse.urlencode(q)

class LingueeExtension(Extension):

    def __init__(self):
        super(LingueeExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = list()

        if event.get_argument():
            LOGGER.info('Word Linguee search for "{}"'.format(event.get_argument()))
            items.append(
                ExtensionResultItem(
                    icon='images/icon.png',
                    name='Define words on Linguee',
                    description='Define words "{}".'.format(event.get_argument()),
                    on_enter=OpenUrlAction(
                        'https://www.linguee.com/' + extension.preferences["lang0"] + "-" + extension.preferences["lang1"] + '/search?{}'.format(urlencode({ 'source': 'auto', 'query': event.get_argument() }))
                    )
                )
            )

            url = "https://linguee-api.herokuapp.com/api"
            query = event.get_argument()
            src = extension.preferences["lang02letter"]
            dst = extension.preferences["lang12letter"]
            params = {'q': query, 'src': src, 'dst': dst}
            response = requests.get(url=url, params=params)
            if response.status_code == 500:
                items.append(
                    ExtensionResultItem(
                        icon='images/icon.png',
                        name='Known problem',
                        description='See https://github.com/imankulov/linguee-api/issues/3',
                        on_enter=CopyToClipboardAction('https://github.com/imankulov/linguee-api/issues/3')
                    )
                )
            if response.status_code == 200:
                examples = response.json()['real_examples']
                for item in examples[0:min(len(examples), 10)]:
                    items.append(
                        ExtensionResultItem(
                            icon='images/icon.png',
                            name=item['src'],
                            description=item['dst'],
                            on_enter=CopyToClipboardAction(item['dst'])
                        )
                    )

        return RenderResultListAction(items)

if __name__ == '__main__':
    LingueeExtension().run()
