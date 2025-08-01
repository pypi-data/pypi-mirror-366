class ArquivoRepository:
    def __init__(self, db):
        self.__db = db

    async def inserir_arquivo(self, arquivo: dict) -> bool:
        
        try:
            arquivo_no_db = await self.__db.arquivos.find_one(
                {"SolicitacaoId": arquivo["solicitacaoId"], "cpf": arquivo["cpf"]}
            )

            if arquivo_no_db is None:
                await self.__db.arquivos.insert_one(arquivo)
                return True

            await self.__db.arquivos.delete_one(
                {"SolicitacaoId": arquivo["solicitacaoId"], "cpf": arquivo["cpf"]}
            )
            await self.__db.arquivos.insert_one(arquivo)
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir o arquivo: {e}")
            return False

    async def remover_arquivo(self, solicitacaoId: int) -> bool:
        try:
            await self.__db.arquivos.delete_many({"SolicitacaoId": solicitacaoId})
            return True
        except Exception as e:
            print(f"❌ Erro ao remover o arquivo: {e}")
            return False
