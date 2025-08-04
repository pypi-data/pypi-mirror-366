import clickhouse_connect

class CliсkHouseClient:
    def __init__(self, host, port, user, password):
        """
        Подключение к ClikHouse
        """
         
        try: 

            self.conn = clickhouse_connect.get_client(
                host=host,
                port=port,                
                user=user,
                password=password,
                verify=False
            )
        except Exception as err:
            raise ConnectionError(f"Ошибка подключения к базе данных: {err}")
    
    def read(self, query):
        """
        Выполняет SQL-запрос для возврата результатов
        :param query: SQL-запрос
        """
        try:
            res = self.conn.command(query) 
            return res
        except Exception as err:
            raise RuntimeError(f"Ошибка выполнения запроса: {err}")
            
            
                    
    def read_pandas(self, query):
        """
        Выполняет SQL-запрос к ClickHouse и возвращает результат в виде pandas.DataFrame.
        """
        try:
            # если библиотека clickhouse-connect >=0.6, есть метод query_df
            df = self.conn.query_df(query)
            return df
        except AttributeError:
            # fallback: вручную собираем DataFrame из сырых данных
            result = self.conn.command(query, with_column_types=True)
            # result — словарь {'meta': [(col, type),...], 'data': [строки...]}
            cols = [col for col, _ in result['meta']]
            return pd.DataFrame(result['data'], columns=cols)
        except Exception as err:
            raise RuntimeError(f"Ошибка чтения в pandas: {err}")

    
    

    def close(self):
        """
        Закрывает соединение с базой данных.
        """
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

