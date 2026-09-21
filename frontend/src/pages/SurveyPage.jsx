import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";
import { useCurrentUser } from "../features/auth/useAuth";
import { useSubmitSurvey, useMySurvey } from "../features/survey/useSurvey";

const QUESTIONS = [
  {
    id: "color",
    type: "select",
    title: "Ваш улюблений колір?",
    options: [
      "Жовтий",
      "Блакитний",
      "Рожевий",
      "Чорний",
      "Білий",
      "Зелений",
      "Фіолетовий",
      "Кораловий",
    ],
  },
  {
    id: "season",
    type: "select",
    title: "Улюблена пора року?",
    options: ["Зима", "Весна", "Літо", "Осінь"],
  },
  {
    id: "childhood",
    type: "opentext",
    title: "Ким ви хотіли стати в дитинстві?",
    placeholder: "Напиши свою відповідь",
  },
  {
    id: "milk",
    type: "select",
    title: "На якому молоці п'єте каву?",
    options: [
      "Бананове",
      "Кокосове",
      "Лавандове",
      "Козяче",
      "Звичайне",
      "П'ю енергетики",
      "Заливаюся чорною кавою",
    ],
  },
  {
    id: "logo",
    type: "select",
    title: "Де більше любите лого/надписи на мерчі?",
    options: ["Спереду", "На спині", "Спереду як значок"],
  },
  {
    id: "drinks",
    type: "multiselect",
    title: "По що з цього бігаєте між парами?",
    hint: "Можна обрати кілька варіантів",
    options: [
      "Кола",
      "Пепсі",
      "Фанта",
      "Квас",
      "Енергетики",
      "Пиво (безалкогольне, ми ж культурні люди)",
    ],
  },
  {
    id: "daytime",
    type: "select",
    title: "Хто ви по часу дня?",
    options: ["Жайворонок", "Сова", "Голуб"],
  },
  {
    id: "tea",
    type: "select",
    title: "Який ви чай?",
    options: ["Чорний", "Зелений", "Lovare", "Нахабний фрукт"],
  },
  {
    id: "tabs",
    type: "select",
    title: "Скільки у вас відкритих вкладок зараз?",
    options: [
      "1-5",
      "6-15",
      "16-30",
      "Не рахую, живу в хаосі",
      "У мене вкладки мають вкладки",
    ],
  },
  {
    id: "alarms",
    type: "select",
    title: "Скільки будильників вам треба, щоб встати на першу пару?",
    options: ["1", "3-5", "10+", "Не встаю, живу за розкладом других пар"],
  },
  {
    id: "transport",
    type: "select",
    title: "Улюблений транспорт до універу?",
    options: ["Маршрутка", "Пішки", "Самокат", "Тролейбус повний людей"],
  },
];

const initialAnswers = QUESTIONS.reduce((acc, question) => {
  acc[question.id] = question.type === "multiselect" ? [] : "";
  return acc;
}, {});

function SurveyPage() {
  const navigate = useNavigate();
  const { user } = useCurrentUser();
  const { survey, isLoading } = useMySurvey();
  const { mutate: submit, isPending } = useSubmitSurvey();
  const [answers, setAnswers] = useState(initialAnswers);
  const isCompleted = Boolean(survey) || Boolean(user?.completed_survey);

  useEffect(() => {
    if (!survey?.answers) return;

    const next = { ...initialAnswers };
    survey.answers.forEach((item) => {
      next[item.id] = item.value;
    });
    setAnswers(next);
  }, [survey]);

  const handleSelect = (id, value) => {
    if (isCompleted) return;
    setAnswers((prev) => ({ ...prev, [id]: value }));
  };

  const handleMultiSelect = (id, value) => {
    if (isCompleted) return;
    setAnswers((prev) => {
      const current = prev[id];
      const next = current.includes(value)
        ? current.filter((item) => item !== value)
        : [...current, value];
      return { ...prev, [id]: next };
    });
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (isCompleted || isPending) return;

    const payload = QUESTIONS.map((question) => ({
      id: question.id,
      title: question.title,
      type: question.type,
      value: answers[question.id],
    }));

    const incomplete = payload.some((item) =>
      Array.isArray(item.value)
        ? item.value.length === 0
        : !String(item.value || "").trim(),
    );

    if (incomplete) {
      alert("Відповідай на всі питання.");
      return;
    }

    submit(
      { answers: payload },
      {
        onSuccess: () => {
          navigate("/survey/reward", {
            state: { celebrate: true, justCompleted: true },
          });
        },
        onError: () => {
          alert("Не вдалося надіслати опитування.");
        },
      },
    );
  };

  if (isLoading) {
    return (
      <main className="survey-page container">
        <p className="survey-subtitle">Завантаження...</p>
      </main>
    );
  }

  return (
    <main className="survey-page container">
      <section className="survey-hero">
        <img src="/cat-curious.png" alt="" className="survey-hero-cat" />
        <div className="survey-hero-copy">
          <div className="survey-badge">ОПИТУВАЛЬНИК ВАЙБУ</div>
          <h1 className="survey-title">Вайб-опитувальник</h1>
          <p className="survey-subtitle">
            {isCompleted
              ? "Опитування вже пройдено. Відповіді лише для перегляду."
              : "Пройди опитування і отримай приємний бонус"}
          </p>
        </div>
      </section>

      {isCompleted && (
        <div className="survey-actions survey-actions--start">
          <button
            type="button"
            className="profile-action-btn survey-submit"
            onClick={() => navigate("/survey/reward")}
          >
            ОБРАТИ СЕТ −15%
          </button>
        </div>
      )}

      <form className="survey-panel" onSubmit={handleSubmit}>
        {QUESTIONS.map((question, index) => (
          <fieldset
            key={question.id}
            className="survey-question"
            disabled={isCompleted}
          >
            <legend className="survey-question-title">
              <span className="survey-question-number">{index + 1}</span>
              {question.title}
            </legend>

            {question.hint && (
              <p className="survey-question-hint">{question.hint}</p>
            )}

            {question.type === "opentext" ? (
              <textarea
                className="survey-textarea"
                name={question.id}
                value={answers[question.id]}
                onChange={(event) =>
                  handleSelect(question.id, event.target.value)
                }
                placeholder={question.placeholder}
                rows={3}
                readOnly={isCompleted}
              />
            ) : (
              <div className="survey-options">
                {question.options.map((option) => {
                  const selected =
                    question.type === "multiselect"
                      ? answers[question.id].includes(option)
                      : answers[question.id] === option;

                  return (
                    <button
                      key={option}
                      type="button"
                      className={`survey-option${selected ? " is-selected" : ""}`}
                      aria-pressed={selected}
                      disabled={isCompleted}
                      onClick={() =>
                        question.type === "multiselect"
                          ? handleMultiSelect(question.id, option)
                          : handleSelect(question.id, option)
                      }
                    >
                      {option}
                    </button>
                  );
                })}
              </div>
            )}
          </fieldset>
        ))}

        {!isCompleted && (
          <div className="survey-actions">
            <button
              type="submit"
              className="profile-action-btn survey-submit"
              disabled={isPending}
            >
              {isPending ? "НАДСИЛАЄМО..." : "НАДІСЛАТИ"}
            </button>
          </div>
        )}
      </form>
    </main>
  );
}

export default SurveyPage;
