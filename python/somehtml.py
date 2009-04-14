import pprint
import sys
import pprint
import re

singletons = ["BR", "AREA", "LINK", "IMG", "PARAM", "HR", "INPUT", "COL", "BASE", "META"]

class GenericTag(object):
	def __init__(self,name="",attrib={},contents="", indented=0):
		self.name     = name
		self.attrib   = attrib
		self.contents = contents
		self.indent   = indented
	def indentstr(self,indent=0):
		return "".join(map(lambda x: "  ",range(indent + self.indent)))
	def attribstr(self):
		return " ".join(map(lambda x: '%s="%s"' % ( re.sub(r'^_','',x),self.attrib[x]), self.attrib.keys()))
	def __repr__(self):
		return "<%s: %s>" % (type(self), self.render())

class OpenTag(GenericTag):
	def render(self,indent=0):
		if self.attrib:
			return self.indentstr() + "<%s %s>\n" % (self.name, self.attribstr())
		else:
			return self.indentstr() + "<%s>\n" % self.name

class SingleTag(GenericTag):
	def render(self,indent=0):
		if self.attrib:
			return self.indentstr() + "<%s %s />\n" % (self.name, self.attribstr())
		else:
			return self.indentstr() + "<%s/>\n" % self.name

class CloseTag(GenericTag):
	def render(self, indent=0):
		return self.indentstr() + "</%s>\n" % self.name

class ItemTag(GenericTag):
	def render(self,indent=0):
		if self.attrib:
			return self.indentstr() + "<%s %s>%s</%s>\n" % (self.name, self.attribstr(), self.contents, self.name)
		else:
			return self.indentstr() + "<%s>%s</%s>\n" % (self.name, self.contents, self.name)

class Text(GenericTag):
	def render(self,indent=0):
		return self.indentstr() + self.contents + "\n"

class HTML(object):

	def __init__(self,indent=0):
		self.indent = indent
		self.before = []
		self.after = []
		self.deck = False

	def getindent(self):
		level = self.indent
		if self.before:
			if isinstance(self.before[-1],OpenTag):
				level = self.before[-1].indent + 1
			else:
				level = self.before[-1].indent
		return level

	def __addtag(self,args=False,kwargs=False):
		if self.deck:
			level = self.getindent()
			if self.deck.upper() in singletons:
				self.before.append(SingleTag(name=self.deck, attrib=kwargs, indented=level))
			elif args:
				self.before.append(ItemTag(name=self.deck, contents=args[0], indented=level,attrib=kwargs))
			else:
				self.before.append(OpenTag(name=self.deck,attrib=kwargs, indented=level))
				self.after.insert(0,CloseTag(name=self.deck,indented=level))

	def __getattr__(self,name):
		if self.deck:
			level = self.getindent()
			self.before.append(OpenTag(name=self.deck, indented=level))
			self.after.insert(0, CloseTag(name=self.deck, indented=level))
		self.deck = name
		return self

	def __call__(self,*args,**kwargs):
		self.__addtag(args=args,kwargs=kwargs)
		self.deck = False
		return self

	def text(self, text):
		level = self.getindent()
		self.before.append(Text(indented=self.getindent(),contents=text))

	def cursor(self):
		newdoc = HTML(indent=self.getindent())
		self.before.append(newdoc)
		return newdoc

	def close(self):
		x = self.after[0]
		del self.after[0]
		self.before.append(x)
		return self

	def render(self):
		out = ''
		for r in self.before:
			out =  out + r.render()
		for r in self.after:
			out = out + r.render() 
		return out

if __name__ == "__main__":
	html = HTML().html
	head = html.head().cursor()
	body = html.close().body().cursor()
	head.title("hi!")
	body.h2("what")
	body.div(_class="honk")
	body.text("what's up?")
	body.hr()
	body.table(border=8)
	for i in range(1,5):
		body.tr()
		for j in range(1,5):
			body.td("%s %s" % ( i,j ))
		body.close() # the tr is still open
			
	print html.render()

