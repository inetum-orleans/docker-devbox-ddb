// Edit me!
{
  person1: {
    name: "Alice",
    welcome: "Hello " + self.name + "!",
  },
  person2: self.person1 { name: std.extVar("old_property"), str: "old_property" },
  person3: self.person1 { name: std.extVar("some.deep.old.property"), str: "some.deep.old.property" }
}