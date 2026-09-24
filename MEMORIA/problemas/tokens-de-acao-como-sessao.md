# Tokens de ação não são tokens de sessão

## Falha evitada

Tokens de verificação de email e recuperação de palavra-passe eram gerados pela
mesma função dos access tokens. Como recebiam `type=access`, podiam ser enviados
como Bearer token e autenticar o utilizador antes de cumprir a ação pretendida.

## Invariante

- Tokens de sessão têm `type=access|refresh`.
- Links de email têm `type=action` e um campo `action` explícito.
- `get_current_user` aceita exclusivamente `type=access`.
- Verificação e reset exigem simultaneamente `type=action` e a ação esperada.
- Manter o teste `test_email_action_token_cannot_authenticate` ao alterar JWT.
