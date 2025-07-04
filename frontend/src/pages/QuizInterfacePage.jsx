import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import QuizInterfaceSimple from '../components/quiz/QuizInterfaceSimple';

const QuizInterfacePage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const handleQuizComplete = (results) => {
    // Handle quiz completion - could show results or redirect
    console.log('Quiz completed with results:', results);
    // Navigate back to quizzes page after completion
    navigate('/quizzes');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <QuizInterfaceSimple 
        quizId={parseInt(id)} 
        onQuizComplete={handleQuizComplete}
      />
    </div>
  );
};

export default QuizInterfacePage;

