from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import func

from app.base.base_accessor import BaseAccessor
from app.questions.models import Answer, AnswerModel, Question, QuestionModel


class QuestionAccessor(BaseAccessor):
    async def create_question(self, question_text: str) -> Question:
        async with self.app.database.session() as session:
            question = QuestionModel(question=question_text)
            session.add(question)
            await session.commit()
            await session.refresh(question)
            return question.to_data()

    async def get_question_by_id(self, question_id: int) -> Question | None:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(QuestionModel)
                .options(selectinload(QuestionModel.answers))
                .where(QuestionModel.id == question_id)
            )
            question_model = result.scalars().first()
            if question_model:
                question = question_model.to_data()
                question.answers = [
                    answer.to_data() for answer in question_model.answers
                ]
                return question
            return None

    async def update_question(
        self, question_id: int, new_text: str
    ) -> Question | None:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(QuestionModel).where(QuestionModel.id == question_id)
            )
            question_model = result.scalars().first()
            if not question_model:
                return None

            question_model.question = new_text
            await session.commit()
            await session.refresh(question_model)
            question = question_model.to_data()
            question.answers = [
                answer.to_data() for answer in question_model.answers
            ]
            return question

    async def delete_question(self, question_id: int) -> bool:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(QuestionModel).where(QuestionModel.id == question_id)
            )
            question_model = result.scalars().first()
            if not question_model:
                return False
            await session.delete(question_model)
            await session.commit()
            return True

    async def get_random_question(self) -> Question | None:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(QuestionModel)
                .options(selectinload(QuestionModel.answers))
                .order_by(func.random())
                .limit(1)
            )
            question_model = result.scalars().first()
            if question_model:
                question = question_model.to_data()
                question.answers = [
                    answer.to_data() for answer in question_model.answers
                ]
                return question
            return None

    async def get_all_questions(self) -> list[Question]:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(QuestionModel).options(
                    selectinload(QuestionModel.answers)
                )
            )
            question_models = result.scalars().all()
            questions = []
            for question_model in question_models:
                question = question_model.to_data()
                question.answers = [
                    answer.to_data() for answer in question_model.answers
                ]
                questions.append(question)
            return questions


class AnswerAccessor(BaseAccessor):
    async def create_answer(
        self, question_id: int, word: str, score: int
    ) -> Answer:
        async with self.app.database.session() as session:
            answer = AnswerModel(
                question_id=question_id, word=word, score=score
            )
            session.add(answer)
            await session.commit()
            await session.refresh(answer)
            return answer.to_data()

    async def get_answers_by_question_id(
        self, question_id: int
    ) -> list[Answer]:
        async with self.app.database.session() as session:
            q = select(AnswerModel).where(
                AnswerModel.question_id == question_id
            )
            result = await session.execute(q)
            answers = result.scalars().all()
            return [answer.to_data() for answer in answers]

    async def get_answer_by_word(
        self, word: str, question_id: int
    ) -> Answer | None:
        async with self.app.database.session() as session:
            q = select(AnswerModel).where(
                func.lower(AnswerModel.word) == word.lower(),
                AnswerModel.question_id == question_id,
            )
            result = await session.execute(q)
            model = result.scalars().first()
            if model:
                return model.to_data()
            return None

    async def check_answer_by_question_id(
        self, question_id: int, answer: str
    ) -> bool:
        async with self.app.database.session() as session:
            q = select(AnswerModel).where(
                AnswerModel.question_id == question_id
            )
            result = await session.execute(q)
            answers = result.scalars().all()
            return any(answer in el.to_data().word for el in answers)

    async def delete_answer(self, answer_id: int) -> bool:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(AnswerModel).where(AnswerModel.id == answer_id)
            )
            answer_model = result.scalars().first()
            if not answer_model:
                return False
            await session.delete(answer_model)
            await session.commit()
            return True

    async def update_answer(
        self, answer_id: int, word: str, score: int
    ) -> Answer | None:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(AnswerModel).where(AnswerModel.id == answer_id)
            )
            answer_model = result.scalars().first()
            if not answer_model:
                return None

            answer_model.word = word
            answer_model.score = score
            await session.commit()
            await session.refresh(answer_model)
            return answer_model.to_data()
