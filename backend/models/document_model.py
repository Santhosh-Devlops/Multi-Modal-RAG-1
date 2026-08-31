import datetime
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, csv, xlsx, png, jpg
    file_size = Column(Integer, default=0)
    domain = Column(String(100), default="General")
    doc_type = Column(String(100), default="Document")
    status = Column(String(50), default="Pending")  # Pending, Processing, Completed, Failed
    page_count = Column(Integer, default=0)
    image_count = Column(Integer, default=0)
    graph_count = Column(Integer, default=0)
    table_count = Column(Integer, default=0)
    numerical_count = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    preview_image_path = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    images = relationship("DocumentImage", back_populates="document", cascade="all, delete-orphan")
    graphs = relationship("DocumentGraph", back_populates="document", cascade="all, delete-orphan")
    tables = relationship("DocumentTable", back_populates="document", cascade="all, delete-orphan")
    numericals = relationship("DocumentNumerical", back_populates="document", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "domain": self.domain,
            "doc_type": self.doc_type,
            "status": self.status,
            "page_count": self.page_count,
            "image_count": self.image_count,
            "graph_count": self.graph_count,
            "table_count": self.table_count,
            "numerical_count": self.numerical_count,
            "chunk_count": self.chunk_count,
            "preview_image_path": self.preview_image_path,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class DocumentPage(Base):
    __tablename__ = "document_pages"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)
    page_text = Column(Text, default="")
    image_count = Column(Integer, default=0)
    graph_count = Column(Integer, default=0)
    table_count = Column(Integer, default=0)
    numerical_count = Column(Integer, default=0)
    preview_image_path = Column(String(500), nullable=True)

    document = relationship("Document", back_populates="pages")

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "page_number": self.page_number,
            "page_text": self.page_text,
            "image_count": self.image_count,
            "graph_count": self.graph_count,
            "table_count": self.table_count,
            "numerical_count": self.numerical_count,
            "preview_image_path": self.preview_image_path
        }

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False, default=1)
    chunk_index = Column(Integer, nullable=False, default=0)
    content_type = Column(String(50), default="text")  # text, image, graph, table, numerical
    content_text = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    domain = Column(String(100), default="General")
    metadata_json = Column(Text, nullable=True)

    document = relationship("Document", back_populates="chunks")

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "page_number": self.page_number,
            "chunk_index": self.chunk_index,
            "content_type": self.content_type,
            "content_text": self.content_text,
            "token_count": self.token_count,
            "domain": self.domain,
            "metadata_json": self.metadata_json
        }

class DocumentImage(Base):
    __tablename__ = "document_images"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False, default=1)
    image_path = Column(String(500), nullable=False)
    image_name = Column(String(255), nullable=True)
    width = Column(Integer, default=0)
    height = Column(Integer, default=0)
    image_type = Column(String(50), default="Diagram")  # Photo, Component Figure, Visual Drawing
    generated_description = Column(Text, nullable=False)
    ocr_text = Column(Text, default="")
    confidence_score = Column(Float, default=0.90)

    document = relationship("Document", back_populates="images")

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "page_number": self.page_number,
            "image_path": self.image_path,
            "image_name": self.image_name,
            "width": self.width,
            "height": self.height,
            "image_type": self.image_type,
            "generated_description": self.generated_description,
            "ocr_text": self.ocr_text,
            "confidence_score": self.confidence_score
        }

class DocumentGraph(Base):
    __tablename__ = "document_graphs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False, default=1)
    graph_type = Column(String(50), default="Process Diagram")  # Bar Chart, Line Graph, Flow Diagram, Architecture Schematic, Pie Chart
    title = Column(String(255), default="Process Flow Diagram")
    labels_json = Column(Text, default="[]")
    axis_info = Column(String(255), default="")
    trend_summary = Column(Text, default="")
    visual_explanation = Column(Text, nullable=False)
    image_path = Column(String(500), nullable=True)

    document = relationship("Document", back_populates="graphs")

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "page_number": self.page_number,
            "graph_type": self.graph_type,
            "title": self.title,
            "labels_json": self.labels_json,
            "axis_info": self.axis_info,
            "trend_summary": self.trend_summary,
            "visual_explanation": self.visual_explanation,
            "image_path": self.image_path
        }

class DocumentTable(Base):
    __tablename__ = "document_tables"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False, default=1)
    table_index = Column(Integer, default=1)
    title = Column(String(255), default="Extracted Table")
    raw_markdown = Column(Text, nullable=False)
    structured_json = Column(Text, nullable=True)
    natural_language_text = Column(Text, nullable=False)
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    image_path = Column(String(500), nullable=True)

    document = relationship("Document", back_populates="tables")

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "page_number": self.page_number,
            "table_index": self.table_index,
            "title": self.title,
            "raw_markdown": self.raw_markdown,
            "structured_json": self.structured_json,
            "natural_language_text": self.natural_language_text,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "image_path": self.image_path
        }

class DocumentNumerical(Base):
    __tablename__ = "document_numericals"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False, default=1)
    parameter_name = Column(String(255), nullable=False)
    numerical_value = Column(String(100), nullable=False)
    unit = Column(String(50), default="")
    category = Column(String(50), default="Measurement")  # Limit, Measurement, Tolerance, Percentage, Equation
    equation_expression = Column(String(255), default="")
    equation_number = Column(String(50), default="")
    context_sentence = Column(Text, nullable=False)

    document = relationship("Document", back_populates="numericals")

    def to_dict(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "page_number": self.page_number,
            "parameter_name": self.parameter_name,
            "numerical_value": self.numerical_value,
            "unit": self.unit,
            "category": self.category,
            "equation_expression": self.equation_expression,
            "equation_number": self.equation_number,
            "context_sentence": self.context_sentence
        }
