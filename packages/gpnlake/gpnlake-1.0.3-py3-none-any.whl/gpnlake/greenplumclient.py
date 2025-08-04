import sqlalchemy
from sqlalchemy import create_engine
import pandas as pd
import psycopg2
import urllib.parse

   
class GreenPlumClient:
    def __init__(self, host, port, dbname, user, password):
        """
        Подключение к PostgreSQL/Greenplum.
        """
        # Экранируем символы в пароле
        quoted_password = urllib.parse.quote_plus(password)
        
        # Создаем строку подключения
        conn_string = f'postgresql://{user}:{quoted_password}@{host}:{port}/{dbname}'
        
        try:
            # Используем SQLAlchemy Engine для поддержки интеграции с Pandas
            self.engine = create_engine(conn_string)
            
            # Дополнительно создаем обычное подключение psycopg2 для выполнения запросов
            self.conn = psycopg2.connect(
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password
            )
        except Exception as err:
            raise ConnectionError(f"Ошибка подключения к базе данных: {err}")
    
    def execute(self, query, params=None, fetch=False):
        """
        Выполняет SQL-запрос с возможностью возвращения результатов.

        :param query: SQL-запрос
        :param params: параметры запроса (tuple/dict)
        :param fetch: если True — вернуть результат
        :return: список словарей с результатами или None
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall()
                else:
                    self.conn.commit()
                    return None
        except psycopg2.Error as err:
            raise RuntimeError(f"Ошибка выполнения запроса: {err}")

    def read_pandas(self, query, params=None):
        """
        Читает данные в DataFrame используя SQLAlchemy engine с возможностью передачи параметров.

        :param query: SQL-запрос (строка или sqlalchemy.text)
        :param params: dict или tuple для параметров запроса
        :return: pandas.DataFrame
        """
        try:
            # pd.read_sql автоматически привязет params к :named_param (для text запросов)
            df = pd.read_sql(sql=query, con=self.engine, params=params)
            return df
        except Exception as err:
            raise RuntimeError(f"Ошибка чтения в pandas: {err}")

    def write_to_table(self, df, table_name, mode='append', schema=None):
        """
        Записывает данные из DataFrame в указанную таблицу базы данных.

        Параметры:
        ----------
        df : pandas.DataFrame
            Датафрейм, содержащий данные для записи.
        
        table_name : str
            Название целевой таблицы в базе данных.
        
        mode : {'append', 'replace'}, default='append'
            Режим записи:
              * append - добавляет новые строки в конце таблицы (если таблица существует);
              * replace - удаляет старую таблицу и создает новую с новыми данными.
        """
    
        try:
            with self.engine.begin() as connection:  # открывает транзакцию и коммитит автоматически
                df.to_sql(table_name, con=connection, index=False, if_exists=mode, schema=schema)
        except Exception as e:
            raise RuntimeError(f"Ошибка при записи данных в таблицу '{table_name}': {e}")

    def close(self):
        """
        Закрывает соединение с базой данных.
        """
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()