    def _processar_blobs(self, entidade: str, service, dict_data: dict, avaliar_diferencas: bool = True, parar_caso_erros: bool = False):

        if entidade in _entidades_blob:
            _campos = _entidades_blob[entidade]
            _ids = [i['id'] for i in dict_data]
            _pk_banco = service._entity_class.pk_field

            self._log(f"Verificando se houve alterações nos blobs da entidade {entidade}.")

            for _campo in _campos:

                _ids_blobs = []
                _file_blobs = []

                if avaliar_diferencas:
                    _ids_to_send_blob = self._api_client.consultar_hash_blob(_ids, entidade, _campo, self.tenant, self.api_key)

                    if len(_ids_to_send_blob) > 0:

                        _hashes_blob_remoto = _ids_to_send_blob['result']

                        _hashes_blob_local = self._integracao_dao().listar_blobs(_pk_banco, _campo, entidade, _ids)

                        # comparar md5
                        for blob_local in _hashes_blob_local:
                            id_local = blob_local['id']
                            hash_local = blob_local['hash']
                            # Procura o hash remoto correspondente
                            hash_remoto = next((item['hash'] for item in _hashes_blob_remoto if item['id'] == id_local), None)
                            if hash_remoto != hash_local:
                                _ids_blobs.append(blob_local['id'])
                                _file_blobs.append(('files', (blob_local['id'], blob_local['blob'], 'application/octet-stream')))
                else:
                    _hashes_blob_local = self._integracao_dao().listar_blobs(_pk_banco, _campo, entidade, _ids)
                    for blob_local in _hashes_blob_local:
                        _ids_blobs.append(blob_local['id'])
                        _file_blobs.append(('files', (blob_local['id'], blob_local['blob'], 'application/octet-stream')))


                self._log(f"Enviando blobs do campo {_campo} para a api.")
                if _ids_blobs:
                    self._enviar_blobs(
                        _ids_blobs,
                        _file_blobs,
                        entidade,
                        _campo,
                        parar_caso_erros
                    )

