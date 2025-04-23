from aiohttp.web_exceptions import HTTPBadRequest, HTTPNotFound
from aiohttp_apispec import docs, request_schema, response_schema

from app.questions.schemes import AnswerSchema, QuestionSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class QuestionAddView(AuthRequiredMixin, View):
    @docs(
        tags=["questions"],
        summary="Add new question",
        description="Create a new question with specified text (Admin only)",
        responses={
            200: {"description": "Question successfully created"},
            401: {"description": "Unauthorized - admin not authenticated"},
        },
    )
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema, 200)
    async def post(self):
        data = await self.request.json()
        question_text = data["question"]
        question = await self.store.questions.create_question(
            question_text=question_text
        )
        return json_response(data=QuestionSchema().dump(question))


class QuestionGetView(View):
    @docs(
        tags=["questions"],
        summary="Get question by ID",
        description="Retrieve question information by ID",
        parameters=[
            {
                "name": "question_id",
                "in": "query",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        responses={
            200: {"description": "Question found successfully"},
            400: {"description": "Invalid question_id parameter"},
            404: {"description": "Question not found"},
        },
    )
    @response_schema(QuestionSchema, 200)
    async def get(self):
        question_id_str = self.request.query.get("question_id")
        if not question_id_str or not question_id_str.isdigit():
            raise HTTPBadRequest(
                text="Parameter 'question_id' is required "
                "and must be an integer."
            )
        question_id = int(question_id_str)
        question = await self.store.questions.get_question_by_id(
            question_id=question_id
        )
        if not question:
            raise HTTPNotFound(
                text=f"Question with id {question_id} not found."
            )
        return json_response(data=QuestionSchema().dump(question))


class AnswerAddView(AuthRequiredMixin, View):
    @docs(
        tags=["questions"],
        summary="Add answer to question",
        description="Add a new answer to a specific question (Admin only)",
        responses={
            200: {"description": "Answer successfully added"},
            401: {"description": "Unauthorized - admin not authenticated"},
            404: {"description": "Question not found"},
        },
    )
    @request_schema(AnswerSchema)
    @response_schema(AnswerSchema, 200)
    async def post(self):
        data = await self.request.json()
        question_id = data["question_id"]
        word = data["word"]
        score = data["score"]

        question = await self.store.questions.get_question_by_id(
            question_id=question_id
        )
        if not question:
            raise HTTPNotFound(
                text=f"Question with id {question_id} not found."
            )
        answer = await self.store.answers.create_answer(
            question_id=question_id, word=word, score=score
        )
        return json_response(data=AnswerSchema().dump(answer))


class AnswerGetView(View):
    @docs(
        tags=["questions"],
        summary="Get answers for question",
        description="Get all answers for a specific question",
        parameters=[
            {
                "name": "question_id",
                "in": "query",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        responses={
            200: {"description": "Answers retrieved successfully"},
            400: {"description": "Invalid question_id parameter"},
            404: {"description": "Question not found"},
        },
    )
    @response_schema(AnswerSchema, 200)
    async def get(self):
        question_id_str = self.request.query.get("question_id")
        if not question_id_str or not question_id_str.isdigit():
            raise HTTPBadRequest(
                text="Parameter 'question_id' is required "
                "and must be an integer."
            )
        question_id = int(question_id_str)
        answers = await self.store.answers.get_answers_by_question_id(
            question_id=question_id
        )
        if not answers:
            raise HTTPNotFound(
                text=f"No answers found for question id {question_id}."
            )
        return json_response(
            data=[AnswerSchema().dump(answer) for answer in answers]
        )


class QuestionDeleteView(AuthRequiredMixin, View):
    @docs(
        tags=["questions"],
        summary="Delete question",
        description="Delete a question by ID (Admin only)",
        parameters=[
            {
                "name": "question_id",
                "in": "query",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        responses={
            200: {"description": "Question successfully deleted"},
            401: {"description": "Unauthorized - admin not authenticated"},
            404: {"description": "Question not found"},
        },
    )
    async def delete(self):
        question_id_str = self.request.query.get("question_id")
        if not question_id_str or not question_id_str.isdigit():
            raise HTTPBadRequest(
                text="Parameter 'question_id' is required "
                "and must be an integer."
            )
        question_id = int(question_id_str)
        success = await self.store.questions.delete_question(
            question_id=question_id
        )
        if not success:
            raise HTTPNotFound(
                text=f"Question with id {question_id} not found."
            )
        return json_response(data={"status": "success"})


class QuestionUpdateView(AuthRequiredMixin, View):
    @docs(
        tags=["questions"],
        summary="Update question",
        description="Update question text by ID (Admin only)",
        parameters=[
            {
                "name": "question_id",
                "in": "query",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        responses={
            200: {"description": "Question successfully updated"},
            401: {"description": "Unauthorized - admin not authenticated"},
            404: {"description": "Question not found"},
        },
    )
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema, 200)
    async def put(self):
        question_id_str = self.request.query.get("question_id")
        if not question_id_str or not question_id_str.isdigit():
            raise HTTPBadRequest(
                text="Parameter 'question_id' is required "
                "and must be an integer."
            )
        question_id = int(question_id_str)

        data = await self.request.json()
        new_text = data["question"]

        question = await self.store.questions.update_question(
            question_id=question_id, new_text=new_text
        )
        if not question:
            raise HTTPNotFound(
                text=f"Question with id {question_id} not found."
            )
        return json_response(data=QuestionSchema().dump(question))


class AnswerDeleteView(AuthRequiredMixin, View):
    @docs(
        tags=["questions"],
        summary="Delete answer",
        description="Delete an answer by ID (Admin only)",
        parameters=[
            {
                "name": "answer_id",
                "in": "query",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        responses={
            200: {"description": "Answer successfully deleted"},
            401: {"description": "Unauthorized - admin not authenticated"},
            404: {"description": "Answer not found"},
        },
    )
    async def delete(self):
        answer_id_str = self.request.query.get("answer_id")
        if not answer_id_str or not answer_id_str.isdigit():
            raise HTTPBadRequest(
                text="Parameter 'answer_id' is required "
                "and must be an integer."
            )
        answer_id = int(answer_id_str)
        success = await self.store.answers.delete_answer(answer_id=answer_id)
        if not success:
            raise HTTPNotFound(text=f"Answer with id {answer_id} not found.")
        return json_response(data={"status": "success"})


class AnswerUpdateView(AuthRequiredMixin, View):
    @docs(
        tags=["questions"],
        summary="Update answer",
        description="Update answer by ID (Admin only)",
        parameters=[
            {
                "name": "answer_id",
                "in": "query",
                "required": True,
                "schema": {"type": "integer"},
            }
        ],
        responses={
            200: {"description": "Answer successfully updated"},
            401: {"description": "Unauthorized - admin not authenticated"},
            404: {"description": "Answer not found"},
        },
    )
    @request_schema(AnswerSchema)
    @response_schema(AnswerSchema, 200)
    async def put(self):
        answer_id_str = self.request.query.get("answer_id")
        if not answer_id_str or not answer_id_str.isdigit():
            raise HTTPBadRequest(
                text="Parameter 'answer_id' is required "
                "and must be an integer."
            )
        answer_id = int(answer_id_str)

        data = await self.request.json()
        word = data["word"]
        score = data["score"]

        answer = await self.store.answers.update_answer(
            answer_id=answer_id, word=word, score=score
        )
        if not answer:
            raise HTTPNotFound(text=f"Answer with id {answer_id} not found.")
        return json_response(data=AnswerSchema().dump(answer))
