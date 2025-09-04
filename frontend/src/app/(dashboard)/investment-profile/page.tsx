'use client';

import { useState } from 'react';
import { Card, CardHeader, CardContent, CardFooter } from '@/design-system/components/Card';
import { Button } from '@/design-system/components/Button';

// Investment Profile Types
interface InvestmentProfile {
  riskTolerance: 'conservative' | 'moderate' | 'aggressive';
  timeHorizon: 'short' | 'medium' | 'long';
  investmentExperience: 'beginner' | 'intermediate' | 'advanced';
  financialGoals: 'preservation' | 'growth' | 'aggressive_growth';
  liquidityNeeds: 'high' | 'medium' | 'low';
  incomeNeeds: 'high' | 'medium' | 'low';
  marketVolatility: 'avoid' | 'tolerate' | 'embrace';
  diversification: 'concentrated' | 'balanced' | 'diversified';
  rebalancing: 'passive' | 'moderate' | 'active';
}

interface Question {
  id: keyof InvestmentProfile;
  title: string;
  description: string;
  options: {
    value: string;
    label: string;
    description: string;
    score: number;
  }[];
}

const questions: Question[] = [
  {
    id: 'riskTolerance',
    title: 'Risk Tolerance',
    description: 'How comfortable are you with investment risk?',
    options: [
      {
        value: 'conservative',
        label: 'Conservative',
        description: 'I prefer stable, low-risk investments with predictable returns',
        score: 1
      },
      {
        value: 'moderate',
        label: 'Moderate',
        description: 'I can handle some risk for potentially higher returns',
        score: 2
      },
      {
        value: 'aggressive',
        label: 'Aggressive',
        description: 'I am comfortable with high risk for potentially high returns',
        score: 3
      }
    ]
  },
  {
    id: 'timeHorizon',
    title: 'Investment Time Horizon',
    description: 'How long do you plan to invest?',
    options: [
      {
        value: 'short',
        label: 'Short-term (1-3 years)',
        description: 'I need access to my money within the next few years',
        score: 1
      },
      {
        value: 'medium',
        label: 'Medium-term (3-10 years)',
        description: 'I can invest for several years before needing the money',
        score: 2
      },
      {
        value: 'long',
        label: 'Long-term (10+ years)',
        description: 'I am investing for retirement or long-term goals',
        score: 3
      }
    ]
  },
  {
    id: 'investmentExperience',
    title: 'Investment Experience',
    description: 'How experienced are you with investing?',
    options: [
      {
        value: 'beginner',
        label: 'Beginner',
        description: 'I am new to investing and prefer simple strategies',
        score: 1
      },
      {
        value: 'intermediate',
        label: 'Intermediate',
        description: 'I have some experience and understand basic concepts',
        score: 2
      },
      {
        value: 'advanced',
        label: 'Advanced',
        description: 'I am experienced and comfortable with complex strategies',
        score: 3
      }
    ]
  },
  {
    id: 'financialGoals',
    title: 'Financial Goals',
    description: 'What is your primary investment objective?',
    options: [
      {
        value: 'preservation',
        label: 'Capital Preservation',
        description: 'I want to protect my money from inflation',
        score: 1
      },
      {
        value: 'growth',
        label: 'Balanced Growth',
        description: 'I want steady growth with some risk',
        score: 2
      },
      {
        value: 'aggressive_growth',
        label: 'Aggressive Growth',
        description: 'I want maximum growth potential',
        score: 3
      }
    ]
  },
  {
    id: 'liquidityNeeds',
    title: 'Liquidity Needs',
    description: 'How quickly might you need access to your investments?',
    options: [
      {
        value: 'high',
        label: 'High Liquidity',
        description: 'I might need quick access to my money',
        score: 1
      },
      {
        value: 'medium',
        label: 'Medium Liquidity',
        description: 'I can plan ahead for most cash needs',
        score: 2
      },
      {
        value: 'low',
        label: 'Low Liquidity',
        description: 'I rarely need quick access to invested funds',
        score: 3
      }
    ]
  },
  {
    id: 'incomeNeeds',
    title: 'Income Needs',
    description: 'Do you need regular income from your investments?',
    options: [
      {
        value: 'high',
        label: 'High Income',
        description: 'I need regular income to cover expenses',
        score: 1
      },
      {
        value: 'medium',
        label: 'Some Income',
        description: 'I would like some income but can reinvest',
        score: 2
      },
      {
        value: 'low',
        label: 'Low Income',
        description: 'I prefer growth over income',
        score: 3
      }
    ]
  },
  {
    id: 'marketVolatility',
    title: 'Market Volatility',
    description: 'How do you react to market volatility?',
    options: [
      {
        value: 'avoid',
        label: 'Avoid Volatility',
        description: 'I prefer stable, predictable investments',
        score: 1
      },
      {
        value: 'tolerate',
        label: 'Tolerate Volatility',
        description: 'I can handle some ups and downs',
        score: 2
      },
      {
        value: 'embrace',
        label: 'Embrace Volatility',
        description: 'I see volatility as opportunity',
        score: 3
      }
    ]
  },
  {
    id: 'diversification',
    title: 'Diversification Preference',
    description: 'How do you prefer to diversify your investments?',
    options: [
      {
        value: 'concentrated',
        label: 'Concentrated',
        description: 'I prefer to focus on a few strong investments',
        score: 1
      },
      {
        value: 'balanced',
        label: 'Balanced',
        description: 'I want a mix of different types of investments',
        score: 2
      },
      {
        value: 'diversified',
        label: 'Highly Diversified',
        description: 'I want broad diversification across many assets',
        score: 3
      }
    ]
  },
  {
    id: 'rebalancing',
    title: 'Portfolio Rebalancing',
    description: 'How actively do you want to manage your portfolio?',
    options: [
      {
        value: 'passive',
        label: 'Passive',
        description: 'I prefer set-and-forget strategies',
        score: 1
      },
      {
        value: 'moderate',
        label: 'Moderate',
        description: 'I want some control but not constant monitoring',
        score: 2
      },
      {
        value: 'active',
        label: 'Active',
        description: 'I want to actively manage and adjust my portfolio',
        score: 3
      }
    ]
  }
];

export default function InvestmentProfilePage() {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Partial<InvestmentProfile>>({});
  const [isComplete, setIsComplete] = useState(false);
  const [riskScore, setRiskScore] = useState(0);

  const handleAnswer = (questionId: keyof InvestmentProfile, value: string) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  const nextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      calculateRiskScore();
      setIsComplete(true);
    }
  };

  const prevQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const calculateRiskScore = () => {
    const totalScore = questions.reduce((sum, question) => {
      const answer = answers[question.id];
      const option = question.options.find(opt => opt.value === answer);
      return sum + (option?.score || 0);
    }, 0);
    
    setRiskScore(totalScore);
  };

  const getRiskProfile = (score: number) => {
    if (score <= 12) return { level: 'Conservative', color: 'text-green-600', bgColor: 'bg-green-50' };
    if (score <= 18) return { level: 'Moderate', color: 'text-yellow-600', bgColor: 'bg-yellow-50' };
    return { level: 'Aggressive', color: 'text-red-600', bgColor: 'bg-red-50' };
  };

  const resetAssessment = () => {
    setCurrentQuestion(0);
    setAnswers({});
    setIsComplete(false);
    setRiskScore(0);
  };

  if (isComplete) {
    const riskProfile = getRiskProfile(riskScore);
    
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Investment Profile Complete!</h1>
          <p className="text-gray-600">Your personalized investment profile has been generated</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Risk Profile Summary */}
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold">Your Risk Profile</h2>
            </CardHeader>
            <CardContent>
              <div className={`p-6 rounded-lg ${riskProfile.bgColor} text-center`}>
                <div className="text-4xl font-bold mb-2">
                  <span className={riskProfile.color}>{riskProfile.level}</span>
                </div>
                <div className="text-2xl font-semibold mb-2">
                  Risk Score: {riskScore}/27
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                  <div 
                    className={`h-3 rounded-full ${
                      riskScore <= 12 ? 'bg-green-500' : 
                      riskScore <= 18 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${(riskScore / 27) * 100}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600">
                  {riskScore <= 12 && "You prefer stable, low-risk investments with predictable returns."}
                  {riskScore > 12 && riskScore <= 18 && "You can handle moderate risk for balanced growth potential."}
                  {riskScore > 18 && "You are comfortable with higher risk for potentially higher returns."}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Recommended Strategies */}
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold">Recommended Strategies</h2>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {riskScore <= 12 && (
                  <>
                    <div className="p-4 bg-green-50 rounded-lg">
                      <h3 className="font-semibold text-green-800">Conservative Portfolio</h3>
                      <p className="text-sm text-green-700">60% Bonds, 30% Large-cap stocks, 10% Cash</p>
                    </div>
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <h3 className="font-semibold text-blue-800">Income Focus</h3>
                      <p className="text-sm text-blue-700">Dividend-paying stocks and bond funds</p>
                    </div>
                  </>
                )}
                {riskScore > 12 && riskScore <= 18 && (
                  <>
                    <div className="p-4 bg-yellow-50 rounded-lg">
                      <h3 className="font-semibold text-yellow-800">Balanced Portfolio</h3>
                      <p className="text-sm text-yellow-700">50% Stocks, 40% Bonds, 10% Alternatives</p>
                    </div>
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <h3 className="font-semibold text-blue-800">Growth & Income</h3>
                      <p className="text-sm text-blue-700">Mix of growth stocks and dividend payers</p>
                    </div>
                  </>
                )}
                {riskScore > 18 && (
                  <>
                    <div className="p-4 bg-red-50 rounded-lg">
                      <h3 className="font-semibold text-red-800">Growth Portfolio</h3>
                      <p className="text-sm text-red-700">70% Stocks, 20% Alternatives, 10% Bonds</p>
                    </div>
                    <div className="p-4 bg-purple-50 rounded-lg">
                      <h3 className="font-semibold text-purple-800">Aggressive Growth</h3>
                      <p className="text-sm text-purple-700">Small-cap and international stocks</p>
                    </div>
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4 mt-8">
          <Button onClick={resetAssessment} variant="outline">
            Retake Assessment
          </Button>
          <Button onClick={() => window.location.href = '/dashboard/portfolio'}>
            Create Portfolio
          </Button>
        </div>
      </div>
    );
  }

  const currentQ = questions[currentQuestion];
  const currentAnswer = answers[currentQ.id];

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Investment Profile Assessment</h1>
        <p className="text-gray-600 mb-4">
          Answer these 9 questions to get your personalized investment profile
        </p>
        
        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
          ></div>
        </div>
        <p className="text-sm text-gray-500">
          Question {currentQuestion + 1} of {questions.length}
        </p>
      </div>

      {/* Question Card */}
      <Card>
        <CardHeader>
          <h2 className="text-2xl font-semibold">{currentQ.title}</h2>
          <p className="text-gray-600">{currentQ.description}</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {currentQ.options.map((option) => (
              <div
                key={option.value}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  currentAnswer === option.value
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => handleAnswer(currentQ.id, option.value)}
              >
                <div className="flex items-start space-x-3">
                  <div className={`w-4 h-4 rounded-full border-2 mt-1 ${
                    currentAnswer === option.value
                      ? 'border-blue-500 bg-blue-500'
                      : 'border-gray-300'
                  }`}>
                    {currentAnswer === option.value && (
                      <div className="w-2 h-2 bg-white rounded-full m-0.5"></div>
                    )}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{option.label}</h3>
                    <p className="text-sm text-gray-600 mt-1">{option.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
        <CardFooter>
          <div className="flex justify-between w-full">
            <Button
              variant="outline"
              onClick={prevQuestion}
              disabled={currentQuestion === 0}
            >
              Previous
            </Button>
            <Button
              onClick={nextQuestion}
              disabled={!currentAnswer}
            >
              {currentQuestion === questions.length - 1 ? 'Complete Assessment' : 'Next'}
            </Button>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
