import aiofiles


async def fill(db, file_path):
    question_answer_dict = {}
    async with aiofiles.open(file_path) as file:
        async for line in file:
            # line_text = await line
            question, answer = line.split(":")
            question_answer_dict[question.lower()] = answer.replace('\n', '').lower()
    await db.create_tables()
    await db.fill_dialog_table(question_answer_dict)
