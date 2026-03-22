export class CreateUser {
  username: string = "";
  password: string = "";
};

export class ChangePassword {
  current_password: string = "";
  new_password: string = "";
};

export class User {
  id: string = "";
  username: string = "";

  constructor(obj?: User) {
    if (obj) {
      this.id = obj.id;
      this.username = obj.username;
    }
  }
};
