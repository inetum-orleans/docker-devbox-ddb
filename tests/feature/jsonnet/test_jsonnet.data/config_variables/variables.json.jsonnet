// Edit me!
{
  person1: {
    name: "Alice",
    welcome: "Hello " + self.name + "!",
  },
  person2: self.person1 { name: std.extVar("var") },
  person3: self.person1 { name: std.extVar("some.deep.nested.variable") },
  person4: self.person1 { name: std.extVar("in.array[1]") },
}