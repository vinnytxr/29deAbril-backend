SELECT n.nspname AS schema,
                   t.relname AS table_name,
                   t.relkind AS type,
                   t.relowner::regrole AS owner
            FROM pg_class AS t
              JOIN pg_namespace AS n ON t.relnamespace = n.oid
            /* only tables and partitioned tables */
            WHERE t.relkind IN ('r', 'p')
              /* exclude system schemas */
              AND n.nspname !~~ ALL ('{pg_catalog,pg_toast,information_schema,pg_temp%}');

CREATE TABLE public.users (
  id SERIAL PRIMARY KEY,
  name VARCHAR,
  email VARCHAR UNIQUE,
  password VARCHAR
);

CREATE TABLE public.roles (
  id SERIAL PRIMARY KEY,
  name VARCHAR
);

CREATE TABLE public.user_roles (
  user_id INTEGER REFERENCES users (id),
  role_id INTEGER REFERENCES roles (id),
  PRIMARY KEY (user_id, role_id)
);

CREATE TABLE public.courses (
  id SERIAL PRIMARY KEY,
  name VARCHAR,
  description VARCHAR,
  professor_id INTEGER REFERENCES users (id)
);

CREATE TABLE public.questions (
  id SERIAL PRIMARY KEY,
  text VARCHAR,
  course_id INTEGER REFERENCES courses (id),
  user_id INTEGER REFERENCES users (id)
);

CREATE TABLE public.answers (
  id SERIAL PRIMARY KEY,
  text VARCHAR,
  question_id INTEGER REFERENCES questions (id),
  user_id INTEGER REFERENCES users (id)
);

-- Insert sample data into users table
INSERT INTO public.users (name, email, password) VALUES
('Alice', 'alice@example.com', 'password1'),
('Bob', 'bob@example.com', 'password2'),
('Charlie', 'charlie@example.com', 'password3'),
('David', 'david@example.com', 'password4'),
('Eve', 'eve@example.com', 'password5'),
('Frank', 'frank@example.com', 'password6'),
('Grace', 'grace@example.com', 'password7'),
('Harry', 'harry@example.com', 'password8'),
('Ivy', 'ivy@example.com', 'password9'),
('John', 'john@example.com', 'password10');

-- Insert sample data into roles table
INSERT INTO public.roles (name) VALUES
('admin'),
('professor'),
('student');

-- Insert sample data into user_roles table
INSERT INTO public.user_roles (user_id, role_id) VALUES
(1, 1),
(2, 2),
(3, 2),
(4, 3),
(5, 3),
(6, 3),
(7, 3),
(8, 3),
(9, 3),
(10, 3);

-- Insert sample data into courses table
INSERT INTO public.courses (name, description, professor_id) VALUES
('History of Rome', 'An overview of the Roman Empire and its legacy', 2),
('Introduction to Computer Science', 'Basic programming concepts and algorithms', 3),
('French Literature', 'Exploring French literature through different periods', 2),
('Artificial Intelligence', 'Exploring the frontiers of machine learning', 3),
('Mathematical Methods in Physics', 'Applying advanced mathematical techniques to solve physical problems', 2),
('Introduction to Psychology', 'Basic principles and theories of psychology', 3),
('Digital Marketing', 'Creating a marketing plan for the digital age', 2),
('Web Development', 'Building dynamic web applications using popular web technologies', 3),
('Public Speaking', 'Mastering the art of public speaking', 2),
('Machine Learning', 'Learning how to build and apply machine learning models', 3);

-- Insert sample data into questions table
INSERT INTO public.questions (text, course_id, user_id) VALUES
('What was the significance of the Roman Empire?', 1, 5),
('What are the main programming paradigms?', 2, 1),
('Who were the major French writers of the 20th century?', 3, 9),
('How can we apply machine learning to financial forecasting?', 4, 7),
('What are some examples of vector calculus in physics?', 5, 4),
('How does the brain process information?', 6, 6),
('What are some effective digital marketing strategies?', 7, 10),
('What are the differences between front-end and back-end web development?', 8, 8),
('How can we overcome stage fright when giving a speech?', 9, 2),
('What are some popular machine learning algorithms?', 10, 3);

-- Insert sample data into answers table
INSERT INTO public.answers (text, question_id, user_id) VALUES
('The Roman Empire had a major impact on the development of Western civilization.', 1, 6),
('The three main paradigms are procedural, functional, and object-oriented programming.', 2, 2),
('Some of the major writers include Albert Camus, Jean-Paul Sartre, and Simone de Beauvoir.', 3, 2);

select * from public.questions;