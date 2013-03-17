#-------------------------------------------------------------------------------
# Name:        engine.py
# Purpose:
#
# Author:      Nelso G. Jost (nelsojost@gmail.com)
#
# Created:     16/09/2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

class AbstractBlock(object):
    def getValueString(self, val):
        """
        Retorna uma string apropriada para "val", conforme este seja um
        valor literal (string) ou um AbstractBlock().
        """
        if isinstance(val, str):
            return val
        elif isinstance(val, FunctionBlock):
            return val.getString()
        else:
            return ""

    def getString(self):
        """
        Retorna a string de código para este bloco.
        """
        return ""

class FunctionBlock(AbstractBlock):
    """
    Define uma classe de blocos que representam comandos como chamadas
    de funções, e portanto, retornam uma string válida para entrada de outras
    funções.
    """
    pass

class InputFunction:
    """
    Define o conteúdo válido para entrada de funções. São eles:

        - string, para valores literais.
        - FunctionBlock(), que representa o retorno de uma função.
        - OperatorBlock(), que representa o retorno de uma operação.
    """
    pass

class Blocks(object):

    class VariableDeclaration(object):
        def __init__(self, type_, name, value=None):
            self.name = name
            self.type = type_
            self.value = value

        def getString(self):
            value = ""
            if self.value is not None:
                value = " = " + self.value
            return self.type + " " + self.name + value


    class Assignment(AbstractBlock):
        def __init__(self, variable, value):
            """
            Bloco de atribuição.

            variable: string. Nome/identificador da variável.
            value: InputFunction. Valor a ser atribuído.
            """
            self.variable = str(variable)
            self.value = value

        def getString(self):
            """
            Retorna uma string na forma: "name = value".
            """
            return self.variable + " = " + self.getValueString(self.value)

    class SkipLines(AbstractBlock):
        def __init__(self, n_lines):
            self.n_lines = n_lines

        def getString(self):
            return "\n"*self.n_lines

    class DigitalWrite(FunctionBlock):
        def __init__(self, pin, value):
            """
            Bloco para escrita digital.

            - pin: InputFunction. Pino digital configurado como "OUTPUT".
            - value: InputFunction. Valor a ser escrito ("HIGH"/"LOW").
            """
            self.pin = pin
            self.value = value

        def getString(self):
            """
            Retorna uma string: "digitalWrite(pin, value)"
            """
            return "digitalWrite(" + self.getValueString(self.pin) + ", " + \
                self.getValueString(self.value) + ")"


    class DigitalRead(FunctionBlock):
        def __init__(self, pin):
            """
            Bloco para leitura digital.

            - pin: InputFunction. Pino digital configurado como "INPUT".
            """
            self.pin = pin

        def getString(self):
            """
            Retorna uma string: "digitalRead(pin)"
            """
            return "digitalRead(" + self.getValueString(self.pin) + ")"


    class Sleep(FunctionBlock):
        def __init__(self, time_ms):
            """
            Bloco para função "espere()".

            - time_ms: InputFunction. Tempo em milisegundos para espera.
            """
            self.time_ms = time_ms

        def getString(self):
            """
            Retorna uma string: "sleep(time_ms)"
            """
            return "sleep(" + self.getValueString(self.time_ms) + ")"

    class PinMode(FunctionBlock):
        """
        Block para configurar um pino como entrada/saída.

        - pin:
        - mode:
        """
        def __init__(self, pin, mode):
            self.pin = pin
            self.mode = mode

        def getString(self):
            return "pinMode(" + self.getValueString(self.pin) + ", " + \
                self.getValueString(self.mode) + ")"


class GroupCode(object):
    """
    Agrupa blocos de função e estruturas.
    """
    def __init__(self, level, app_groups):
        self._blocks = []
        self.level = level
        self.indentation = "    "

        app_groups[id(self)] = self

    def getString(self):
        code = ""
        for x in self._blocks:
            if isinstance(x, Blocks.SkipLines):
                code += x.getString()
            else:
                code += self.indentation*self.level + x.getString()
                if not isinstance(x, Structure.IfElse):
                    code += ";"
                code += "\n"
        return code

    def addBlock(self, block):
        self._blocks.append(block)
        if isinstance(block, Structure.IfElse):
            return id(block.if_branch), id(block.else_branch)


class Structure:

    class Function(object):
        """
        Mantém uma estrutura de sub-rotina, com separação da área para
        declaração de variáveis locais e o código em si.
        """
        def __init__(self, name, type_, params, app_groups):
            self.name = name
            self.type = type_
            self.params = params
            self._locals = GroupCode(1, app_groups)   # local variables
            self._code = GroupCode(1, app_groups)

        def getString(self):
            return self.type + " " + self.name + "(" + self.params + \
                ") {\n" + self._code.getString() + "}"


    class IfElse(object):
        """
        Mantém uma estrutura if-else com múltiplas bifurcações.
        Cada bifurcação mantém o código em um objeto GroupCode().
        """
        def __init__(self, condition, parent_group, app_groups, branch_type=0):
            self.condition = condition
            self.level = parent_group.level
            self.branch_type = branch_type

            self.indentation = "    "

            self.if_branch = GroupCode(self.level + 1, app_groups)
            self.else_branch = GroupCode(self.level + 1, app_groups)


        def getString(self):
            ind = self.indentation*self.level   # indentation

            code = "if (" + str(self.condition) + ") {\n" + \
                self.if_branch.getString() + ind + "}"

            if self.branch_type == 1:
                code += " else {\n" + self.else_branch.getString() + ind + "}"

            return code + "\n"



class TheProgram(object):

    def __init__(self):
        self._groups = {}

        self._cons = GroupCode(0, self._groups)
        self._vars = GroupCode(0, self._groups)
        self._functions = []
        self._functions.append(Structure.Function("setup", "void", "",
            self._groups))
        self._functions.append(Structure.Function("loop", "void", "",
            self._groups))



    def addGlobalConstant(self, type_, name, value):
        """
        Adiciona um bloco de declaração de constante global.
        """
        self._cons.addBlock(Blocks.VariableDeclaration("const " + type_,
            value))


    def addGlobalVariable(self, type_, name, value=None):
        """
        Adiciona um bloco de declaração de variável global.
        """
        self._vars.addBlock(Blocks.VariableDeclaration(type_, name, value))


    def addBlockToFunction(self, function_name, block):
        """
        Adiciona um bloco à uma função dado o nome da mesma.
        """
        for func in self._functions:
            if func.name == function_name:
                return func._code.addBlock(block)

    def addBlockToGroup(self, group_id, block):
        """
        Adiciona um bloco a um grupo segundo a ID fornecida.
        """
        self._groups[group_id].addBlock(block)


    def getString(self):
        """
        Retorna a string completa do código do programa na linguagem C-like
        do Arduino.

        Pode ser transferido para a IDE padrão do Arduino e subsequênte
        compilação.
        """
        code = self._cons.getString() + "\n" + self._vars.getString() + "\n"
        for func in self._functions:
            code += func.getString() + "\n\n"
        return code

    def getFunctionGroup(self, function_name):
        """
        Retorna um GroupCode() que contém o código de uma função.
        """
        for func in self._functions:
            if func.name == function_name:
                return func._code


    def loadExample(self, name):
        """
        Exemplos disponíveis para teste:
            - blink
            - button
        """
        if name == "blink":
            self.__init__()
            self.addGlobalVariable("int", "ledPin", "13")

            self.addBlockToFunction("setup",
                Blocks.PinMode("ledPin", "OUTPUT"))

            self.addBlockToFunction("loop",
                Blocks.DigitalWrite("ledPin", "HIGH"))

            self.addBlockToFunction("loop",
                Blocks.Sleep("1000"))

            self.addBlockToFunction("loop",
                Blocks.DigitalWrite("ledPin", "LOW"))

            self.addBlockToFunction("loop",
                Blocks.Sleep("1000"))


        elif name == "button":
            self.__init__()
            self.addGlobalConstant("int", "buttonPin", "2")
            self.addGlobalConstant("int", "ledPin", "13")
            self.addGlobalVariable("int", "buttonState", "0")

            self.addBlockToFunction("setup",
                Blocks.PinMode("ledPin", "OUTPUT"))

            self.addBlockToFunction("setup",
                Blocks.PinMode("buttonPin", "INPUT"))

            self.addBlockToFunction("loop",
                Blocks.Assignment("buttonState",
                    Blocks.DigitalRead("buttonPin")))

            self.addBlockToFunction("loop", Blocks.SkipLines(1))

            if_b, else_b = self.addBlockToFunction("loop",
                Structure.IfElse("buttonState == HIGH",
                self.getFunctionGroup("loop"), self._groups, 1))

            self.addBlockToGroup(if_b, Blocks.DigitalWrite("ledPin", "HIGH"))
            self.addBlockToGroup(else_b, Blocks.DigitalWrite("ledPin", "LOW"))



if __name__ == "__main__":
    app = TheProgram()
    app.loadExample("button")
    print app.getString()


