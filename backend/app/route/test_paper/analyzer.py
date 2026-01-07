from app.models.question import Question

def calculate_score(quiz_id, user_answers):
    """
    Calculates the score for a given quiz submission.
    
    Args:
        quiz_id (int): ID of the quiz.
        user_answers (dist): Dictionary mapping question_id (str) to selected_option (str).
                               For multi-select, selected_option might be "1,2".

    Returns:
        dict: {
            "total_score": int,
            "max_score": int,
            "correct_count": int,
            "wrong_count": int,
            "results": list of dicts (details for each question)
        }
    """
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    total_score = 0
    max_score = len(questions) # Assuming 1 point per question for now
    correct_count = 0
    wrong_count = 0
    results = []

    for question in questions:
        qid_str = str(question.id)
        user_ans = user_answers.get(qid_str) # Expecting string "1" or "1,2"
        
        is_correct = False
        
        # Determine if answer is correct
        # For both single and multi, we compare the sanitized strings
        # Multi-select "1,2" == "1,2" (order matters if simple string compare, 
        # but usually UI sends sorted or we ensure storage is sorted)
        # For robustness, we can split and set compare for multi type
        
        if user_ans:
            if question.question_type == "multi":
                # Convert "1,2" -> {"1", "2"}
                db_opts = set(question.correct_option.split(','))
                user_opts = set(user_ans.split(','))
                if db_opts == user_opts:
                    is_correct = True
            else:
                # Single choice, direct string comparison
                if user_ans == question.correct_option:
                    is_correct = True
        
        if is_correct:
            total_score += 1
            correct_count += 1
        else:
            wrong_count += 1

        results.append({
            "question_id": question.id,
            "user_answer": user_ans,
            "correct_answer": question.correct_option,
            "is_correct": is_correct
        })

    return {
        "total_score": total_score,
        "max_score": max_score,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "results": results
    }
