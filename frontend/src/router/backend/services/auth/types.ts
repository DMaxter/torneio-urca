export class LoginCredentials {
  username: string = "";
  password: string = "";
}

export class Token {
  access_token: string = "";
  token_type: string = "bearer";
}

export class CurrentUser {
  username: string = "";
  user_id: string = "";
}
