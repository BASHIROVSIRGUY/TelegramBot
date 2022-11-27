# import spacy
from pyaspeller import YandexSpeller
from pymorphy2 import MorphAnalyzer
import re
from models.database import DataBase


class AnswerChooser:
    potential_question_from_db_dict = {}
    # _nlp = spacy.load("ru_core_news_sm")
    _speller = YandexSpeller()
    _morpholog = MorphAnalyzer()

    def __init__(self, loop):
        self.loop = loop
        self.db = self.loop.run_until_complete(DataBase.get_db_obj(self.loop))

    async def get_answer(self, question: str) -> str | None:
        self.potential_question_from_db_dict = {}
        question = re.sub(r'[^А-ЯЁа-яё\s]|\s{2,}', '', question).lower()
        answer = await self.find_answer_by_question(question)
        if answer is None:
            question_from_db_id = await self._choose_question(question)
            answer = await self.find_answer_by_id(question_from_db_id) if question_from_db_id else None
        return answer

    async def find_answer_by_question(self, question: str) -> str:
        return await self.db.select_answer_by_question(question+"?")

    async def find_answer_by_id(self, question_id: str | int) -> str:
        return await self.db.select_answer_by_id(int(question_id))

    async def _choose_question(self, question_user_text: str) -> str:
        tag_list = await self.loop.run_in_executor(None, self._get_normalize_set, question_user_text)
        question_list_from_db = await self.db.select_question_dict_like_tag_list(tag_list=tag_list)
        right_question_from_db_id = None
        for question_id, question_text in question_list_from_db.items():
            if await self._compare_string(question_text, question_user_text):
                right_question_from_db_id = question_id # выбирается тот вопрос из базы, который содержится в вопросе пользователя
                break
            elif await self._compare_string(question_user_text, question_text):
                self.potential_question_from_db_dict[question_id] = question_text # создаётся массив потенциальных вопросов, в которых содержится вопрос пользователя, предполагается выводить их списком как кнопки
        return right_question_from_db_id

    async def _compare_string(self, s1: str, s2: str) -> bool:
        proposition1 = await self.loop.run_in_executor(None, self._get_normalize_set, s1)
        proposition2 = await self.loop.run_in_executor(None, self._get_normalize_set, s2)
        return proposition1 <= proposition2

    def _get_normalize_set(self, text: str) -> set:
        def prepare(word: str) -> str:
            edits = list(self._speller.spell(word))
            if len(edits) > 0:
                word = edits[0]['s'][0]
            billet = self._morpholog.parse(word)
            word = billet[0].normal_form
            return word
        text = re.sub(r'[^А-ЯЁа-яё\s]|\s{2,}', '', text).lower()
        word_set = set(map(prepare, text.split()))
        return word_set

    def __del__(self):
        if self.loop:
            self.loop.close()

    # async def _choose_question(self, question: str) -> int:
    #     tag_list = question.split()
    #     question_list_from_db = await self.db.select_question_dict_like_tag_list(tag_list=tag_list)
    #     right_question_from_db_id = None
    #     for question_id, question_from_db in question_list_from_db.items():
    #         ratio = await dp.loop.run_in_executor(None, self._compare_string, question_from_db, question)
    #         if ratio >= 70:
    #             right_question_from_db_id = question_id
    #         elif ratio >= 50:
    #             self.potential_question_list_from_db.append(question_id)
    #     return right_question_from_db_id

    # def _compare_string(self, s1: str, s2: str) -> float:
    #     proposition1 = self._nlp(s1)
    #     proposition2 = self._nlp(s2)
    #     return proposition1.similarity(proposition2)

