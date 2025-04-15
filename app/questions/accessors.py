from sqlalchemy import select
from app.base.base_accessor import BaseAccessor
from app.questions.models import QuestionModel, Question, AnswerModel, Answer
from sqlalchemy.orm import selectinload

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
                question.answers = [answer.to_data() for answer in question_model.answers]
                return question
            return None

class AnswerAccessor(BaseAccessor):
    async def create_answer(self, question_id: int, word: str, score: int) -> Answer:
        async with self.app.database.session() as session:
            answer = AnswerModel(question_id=question_id, word=word, score=score)
            session.add(answer)
            await session.commit()
            await session.refresh(answer)
            return answer.to_data()

    async def get_answers_by_question_id(self, question_id: int) -> list[Answer]:
        async with self.app.database.session() as session:
            q = select(AnswerModel).where(AnswerModel.question_id == question_id)
            result = await session.execute(q)
            answers = result.scalars().all()
            return [answer.to_data() for answer in answers]
        
    async def check_answer_by_question_id(self, question_id: int, answer: str) -> bool:
        async with self.app.database.session() as session:
            q = select(AnswerModel).where(AnswerModel.question_id == question_id)
            result = await session.execute(q)
            answers = result.scalars().all()
            if answer in answers:
                return True
            return False